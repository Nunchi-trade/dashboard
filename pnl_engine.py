"""
Nunchi Dashboard - PnL Engine
Calculate cumulative PnL from TEE trade logs (DecisionEnvelope / ClearingEnvelope JSONL).
Used by the LVR Defense tab to compare Nunchi Shadow PnL vs HLP vault performance.
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional

import pandas as pd
import requests


class PnLEngine:
    """Calculate cumulative PnL from TEE trade logs."""

    def __init__(self, solver_id: str = "solver-A"):
        self.solver_id = solver_id

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_decision_log(self, path_or_url: str) -> List[Dict]:
        """Load DecisionEnvelope JSONL from local file or URL."""
        lines = self._read_jsonl(path_or_url)
        return lines

    def load_clearing_log(self, path_or_url: str) -> List[Dict]:
        """Load ClearingEnvelope JSONL from local file or URL."""
        lines = self._read_jsonl(path_or_url)
        return lines

    def _read_jsonl(self, path_or_url: str) -> List[Dict]:
        """Read JSONL from a local file path or HTTP(S) URL."""
        raw_lines: List[str] = []

        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            try:
                resp = requests.get(path_or_url, timeout=30)
                resp.raise_for_status()
                raw_lines = resp.text.strip().splitlines()
            except Exception as e:
                print(f"PnLEngine: failed to fetch {path_or_url}: {e}")
                return []
        else:
            if not os.path.exists(path_or_url):
                print(f"PnLEngine: file not found: {path_or_url}")
                return []
            with open(path_or_url, "r") as f:
                raw_lines = f.readlines()

        results: List[Dict] = []
        for i, line in enumerate(raw_lines):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"PnLEngine: bad JSON on line {i}: {e}")
        return results

    # ------------------------------------------------------------------
    # PnL Computation (from clearing log)
    # ------------------------------------------------------------------

    def compute_cumulative_pnl(self, clearing_log: List[Dict]) -> pd.DataFrame:
        """
        From clearing-round fills, compute mark-to-market PnL for the
        configured solver (default solver-A = Nunchi House Agent).

        Tracks running inventory position and average entry cost.
        Realized PnL is booked when position is reduced.
        Unrealized PnL is marked at each round's clearing price.

        Returns DataFrame with columns:
            [timestamp, round_id, clearing_price, position, realized_pnl,
             unrealized_pnl, total_pnl, cumulative_pnl]
        """
        if not clearing_log:
            return pd.DataFrame()

        rows: List[Dict] = []
        position = 0.0        # net ETH position (positive = long)
        avg_entry = 0.0       # average cost basis
        realized_pnl = 0.0    # cumulative realized PnL ($)

        for entry in clearing_log:
            envelope = entry.get("envelope", entry)
            clearing_result = envelope.get("clearing_result", {})
            round_id = clearing_result.get("round_id", entry.get("round_id", ""))
            fills = clearing_result.get("fills", [])

            # Determine clearing price (use first instrument)
            instruments = clearing_result.get("instruments", {})
            clearing_price = 0.0
            for _inst, info in instruments.items():
                clearing_price = float(info.get("clearing_price", 0))
                break

            # Parse timestamp
            ts_str = clearing_result.get("timestamp")
            ts_ms = entry.get("timestamp_ms")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    ts = datetime.now(timezone.utc)
            elif ts_ms:
                ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            else:
                ts = datetime.now(timezone.utc)

            # Process fills for the target solver
            round_pnl = 0.0
            for fill in fills:
                if fill.get("solver_id") != self.solver_id:
                    continue
                qty_filled = float(fill.get("quantity_filled", 0))
                if qty_filled <= 0:
                    continue
                fill_price = float(fill.get("fill_price", 0))
                if fill_price <= 0:
                    continue

                side = fill.get("side", "")

                if side == "buy":
                    # Buying: if currently short, this reduces position (realize PnL)
                    if position < 0:
                        close_qty = min(qty_filled, abs(position))
                        # Short was entered at avg_entry, closing at fill_price
                        pnl = (avg_entry - fill_price) * close_qty
                        realized_pnl += pnl
                        round_pnl += pnl
                        remaining = qty_filled - close_qty

                        # Update position
                        position += close_qty
                        if remaining > 0:
                            # Flipping to long
                            if position == 0:
                                avg_entry = fill_price
                            else:
                                avg_entry = (
                                    (avg_entry * abs(position) + fill_price * remaining)
                                    / (abs(position) + remaining)
                                )
                            position += remaining
                    else:
                        # Adding to long or opening new long
                        if position == 0:
                            avg_entry = fill_price
                        else:
                            avg_entry = (
                                (avg_entry * position + fill_price * qty_filled)
                                / (position + qty_filled)
                            )
                        position += qty_filled

                elif side == "sell":
                    # Selling: if currently long, this reduces position (realize PnL)
                    if position > 0:
                        close_qty = min(qty_filled, position)
                        # Long was entered at avg_entry, closing at fill_price
                        pnl = (fill_price - avg_entry) * close_qty
                        realized_pnl += pnl
                        round_pnl += pnl
                        remaining = qty_filled - close_qty

                        # Update position
                        position -= close_qty
                        if remaining > 0:
                            # Flipping to short
                            if position == 0:
                                avg_entry = fill_price
                            else:
                                avg_entry = (
                                    (avg_entry * abs(position) + fill_price * remaining)
                                    / (abs(position) + remaining)
                                )
                            position -= remaining
                    else:
                        # Adding to short or opening new short
                        if position == 0:
                            avg_entry = fill_price
                        else:
                            avg_entry = (
                                (avg_entry * abs(position) + fill_price * qty_filled)
                                / (abs(position) + qty_filled)
                            )
                        position -= qty_filled

            # Unrealized PnL on remaining position
            if position > 0:
                unrealized = (clearing_price - avg_entry) * position
            elif position < 0:
                unrealized = (avg_entry - clearing_price) * abs(position)
            else:
                unrealized = 0.0

            total_pnl = realized_pnl + unrealized

            rows.append({
                "timestamp": ts,
                "round_id": round_id,
                "clearing_price": clearing_price,
                "position": round(position, 6),
                "trade_pnl": round(round_pnl, 4),
                "realized_pnl": round(realized_pnl, 4),
                "unrealized_pnl": round(unrealized, 4),
                "total_pnl": round(total_pnl, 4),
                "cumulative_pnl": round(total_pnl, 4),
            })

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        # Convert cumulative_pnl to percentage return
        # Use notional capital = first clearing_price * 1 ETH as base
        if df["clearing_price"].iloc[0] > 0:
            notional = df["clearing_price"].iloc[0]  # ~$2500
            df["cumulative_pnl"] = (df["total_pnl"] / notional) * 100
        return df

    def compute_daily_returns(self, pnl_df: pd.DataFrame) -> pd.DataFrame:
        """Daily return series for comparison."""
        if pnl_df.empty:
            return pd.DataFrame()

        df = pnl_df.copy()
        df = df.set_index("timestamp")
        daily = df["cumulative_pnl"].resample("1D").last().dropna()
        daily_returns = daily.diff().fillna(daily.iloc[0] if len(daily) > 0 else 0)

        return pd.DataFrame({
            "timestamp": daily.index,
            "cumulative_pnl": daily.values,
            "daily_return": daily_returns.values,
        }).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Attestation Table (for proof viewer)
    # ------------------------------------------------------------------

    def get_attestation_table(self, clearing_log: List[Dict]) -> pd.DataFrame:
        """
        Extract per-round attestation summary for the proof viewer.

        Returns DataFrame with display columns + hidden detail columns:
            Display: [Timestamp, Round, Fills, Price, Volume, PCR0, Status]
            Detail:  [result_hash, signature, pcr0, pcr1, pcr2, prev_hash,
                      attestation_doc, verification_checks]
        """
        if not clearing_log:
            return pd.DataFrame()

        rows: List[Dict] = []
        round_counter = 0

        for entry in clearing_log:
            envelope = entry.get("envelope", entry)
            clearing_result = envelope.get("clearing_result", {})
            round_id = clearing_result.get("round_id", entry.get("round_id", ""))
            verification = entry.get("verification", {})

            # Timestamp
            ts_str = clearing_result.get("timestamp", "")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    ts_display = ts.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    ts_display = ts_str
            else:
                ts_display = "N/A"

            # Clearing price + volume from instruments
            instruments = clearing_result.get("instruments", {})
            price_str = "N/A"
            volume_str = "0"
            for _inst, info in instruments.items():
                price_str = f"${float(info.get('clearing_price', 0)):,.2f}"
                volume_str = f"{float(info.get('total_volume', 0)):.1f} ETH"

            # Fill summary
            fills = clearing_result.get("fills", [])
            filled_count = sum(1 for f in fills if float(f.get("quantity_filled", 0)) > 0)
            total_fills = len(fills)
            fills_str = f"{filled_count}/{total_fills}"

            # Attestation details
            attestation = envelope.get("attestation", {})
            pcrs = attestation.get("pcrs", {})
            pcr0_full = pcrs.get("0", "N/A")
            pcr0_truncated = pcr0_full[:16] + "..." if len(pcr0_full) > 16 else pcr0_full

            # Verification status
            is_verified = verification.get("ok", False)
            checks = verification.get("checks", {})
            passed = sum(1 for v in checks.values() if v)
            total_checks = len(checks)
            if is_verified:
                status = f"Verified ({passed}/{total_checks})"
            elif total_checks > 0:
                status = f"Partial ({passed}/{total_checks})"
            else:
                status = "Unverified"

            rows.append({
                # Display columns
                "Timestamp": ts_display,
                "Round": round_counter,
                "Round ID": round_id,
                "Fills": fills_str,
                "Price": price_str,
                "Volume": volume_str,
                "PCR0": pcr0_truncated,
                "Status": status,
                # Detail columns (for expander)
                "result_hash": envelope.get("clearing_result_hash", "N/A"),
                "signature": envelope.get("agent_signature", "N/A"),
                "pcr0": pcrs.get("0", "N/A"),
                "pcr1": pcrs.get("1", "N/A"),
                "pcr2": pcrs.get("2", "N/A"),
                "prev_hash": envelope.get("prev_envelope_hash") or "null (genesis)",
                "attestation_doc": attestation.get("document", "N/A"),
                "verification_checks": json.dumps(checks, indent=2) if checks else "{}",
            })

            round_counter += 1

        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Alignment helper
    # ------------------------------------------------------------------

    def align_nunchi_hlp(
        self, nunchi_pnl: pd.DataFrame, hlp_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Align Nunchi PnL and HLP return series on the same time axis.
        Useful for computing correlation or overlaying on a single chart.
        """
        if nunchi_pnl.empty or hlp_df.empty:
            return pd.DataFrame()

        nunchi = nunchi_pnl[["timestamp", "cumulative_pnl"]].copy()
        nunchi = nunchi.rename(columns={"cumulative_pnl": "nunchi_return"})
        nunchi = nunchi.set_index("timestamp")

        hlp = hlp_df[["timestamp", "cumulative_return"]].copy()
        hlp = hlp.rename(columns={"cumulative_return": "hlp_return"})
        hlp = hlp.set_index("timestamp")

        merged = nunchi.join(hlp, how="outer").sort_index()
        merged = merged.ffill().bfill()
        return merged.reset_index()
