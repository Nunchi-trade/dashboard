"""
Nunchi Dashboard - HyperEVM Data Fetcher
Queries blockchain events directly from HyperEVM RPC
Uses requests instead of web3.py to avoid asyncio issues with Streamlit
"""

import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from cachetools import TTLCache

import json
import os

from config import (
    RPC_URL, CONTRACTS, EVENTS, ZERO_ADDRESS, CACHE_TTL, TOKEN_DECIMALS, PENDLE_MARKETS
)

# Calculate divisor for token amounts
TOKEN_DIVISOR = 10 ** TOKEN_DECIMALS

# Cache for expensive queries
_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)

# File path for persistent all-time totals cache
ALLTIME_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'alltime_cache.json')

# Starting blocks for contracts (discovered via binary search)
CONTRACT_START_BLOCKS = {
    'wNLP': 20000000,
    'SY_wNLP': 20000000,
    'PENDLE_MARKET_DEC': 20000000,
    'PENDLE_MARKET_JUN': 24000000,
}


def rpc_call(method: str, params: list) -> dict:
    """Make a JSON-RPC call to HyperEVM"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }

    try:
        response = requests.post(RPC_URL, json=payload, timeout=30)
        result = response.json()
        if "error" in result:
            print(f"RPC Error: {result['error']}")
            return {}
        return result.get("result", {})
    except Exception as e:
        print(f"RPC call failed: {e}")
        return {}


def get_current_block() -> int:
    """Get current block number"""
    result = rpc_call("eth_blockNumber", [])
    if result:
        return int(result, 16)
    return 0


def get_block_timestamp(block_num: int) -> int:
    """Get timestamp for a specific block"""
    result = rpc_call("eth_getBlockByNumber", [hex(block_num), False])
    if result and "timestamp" in result:
        return int(result["timestamp"], 16)
    return int(time.time())


def get_block_by_timestamp(target_timestamp: int) -> int:
    """Estimate block number for a given timestamp"""
    current_block = get_current_block()
    if current_block == 0:
        return 1

    current_time = get_block_timestamp(current_block)

    # Estimate blocks per second (HyperEVM ~2 second blocks)
    blocks_per_second = 0.5
    time_diff = current_time - target_timestamp
    estimated_block = max(1, int(current_block - (time_diff * blocks_per_second)))

    return estimated_block


def fetch_logs(
    contract_address: str,
    topics: List[str],
    from_block: int,
    to_block: int = None,
    batch_size: int = 900
) -> List[Dict]:
    """Fetch event logs from HyperEVM"""
    if to_block is None:
        to_block = get_current_block()

    if to_block == 0:
        return []

    all_logs = []
    current_from = from_block

    while current_from <= to_block:
        current_to = min(current_from + batch_size, to_block)

        params = [{
            "fromBlock": hex(current_from),
            "toBlock": hex(current_to),
            "address": contract_address,
            "topics": topics,
        }]

        result = rpc_call("eth_getLogs", params)

        if isinstance(result, list):
            for log in result:
                all_logs.append({
                    'block_number': int(log['blockNumber'], 16),
                    'tx_hash': log['transactionHash'],
                    'log_index': int(log['logIndex'], 16),
                    'address': log['address'],
                    'topics': log['topics'],
                    'data': log.get('data', '0x'),
                })

        time.sleep(0.1)  # Rate limiting
        current_from = current_to + 1

    return all_logs


def decode_uint256(hex_data: str, offset: int = 0) -> int:
    """Decode uint256 from hex data"""
    if not hex_data or hex_data == '0x':
        return 0
    if hex_data.startswith('0x'):
        hex_data = hex_data[2:]
    start = offset * 64
    end = start + 64
    if len(hex_data) < end:
        return 0
    return int(hex_data[start:end], 16)


def decode_int256(hex_data: str, offset: int = 0) -> int:
    """Decode int256 from hex data (signed)"""
    value = decode_uint256(hex_data, offset)
    if value >= 2**255:
        value -= 2**256
    return value


def decode_address(topic: str) -> str:
    """Decode address from topic (last 40 chars)"""
    if not topic:
        return ZERO_ADDRESS
    if topic.startswith('0x'):
        topic = topic[2:]
    return '0x' + topic[-40:]


def add_block_timestamps(logs: List[Dict]) -> List[Dict]:
    """Add timestamps to logs"""
    block_times = {}

    for log in logs:
        block_num = log['block_number']
        if block_num not in block_times:
            ts = get_block_timestamp(block_num)
            block_times[block_num] = datetime.fromtimestamp(ts)
            time.sleep(0.05)  # Rate limiting

    for log in logs:
        log['timestamp'] = block_times.get(log['block_number'], datetime.now())

    return logs


# ============================================================================
# DATA FETCHING FUNCTIONS
# ============================================================================

def get_nlp_transfers(days: int = 30) -> pd.DataFrame:
    """Get wNLP token transfers"""
    cache_key = f"nlp_transfers_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    from_block = get_block_by_timestamp(
        int((datetime.now() - timedelta(days=days)).timestamp())
    )

    logs = fetch_logs(
        CONTRACTS['wNLP'],
        [EVENTS['TRANSFER']],
        from_block
    )

    if not logs:
        return pd.DataFrame()

    logs = add_block_timestamps(logs)

    data = []
    for log in logs:
        from_addr = decode_address(log['topics'][1]) if len(log['topics']) > 1 else ZERO_ADDRESS
        to_addr = decode_address(log['topics'][2]) if len(log['topics']) > 2 else ZERO_ADDRESS
        amount = decode_uint256(log['data']) / TOKEN_DIVISOR

        transfer_type = 'transfer'
        if from_addr.lower() == ZERO_ADDRESS.lower():
            transfer_type = 'mint'
        elif to_addr.lower() == ZERO_ADDRESS.lower():
            transfer_type = 'burn'

        data.append({
            'timestamp': log['timestamp'],
            'block': log['block_number'],
            'tx_hash': log['tx_hash'],
            'from': from_addr,
            'to': to_addr,
            'amount': amount,
            'type': transfer_type,
        })

    df = pd.DataFrame(data)
    _cache[cache_key] = df
    return df


def get_sy_transfers(days: int = 30) -> pd.DataFrame:
    """Get SY-wNLP transfers (Pendle deposits/withdrawals)"""
    cache_key = f"sy_transfers_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    from_block = get_block_by_timestamp(
        int((datetime.now() - timedelta(days=days)).timestamp())
    )

    logs = fetch_logs(
        CONTRACTS['SY_wNLP'],
        [EVENTS['TRANSFER']],
        from_block
    )

    if not logs:
        return pd.DataFrame()

    logs = add_block_timestamps(logs)

    data = []
    for log in logs:
        from_addr = decode_address(log['topics'][1]) if len(log['topics']) > 1 else ZERO_ADDRESS
        to_addr = decode_address(log['topics'][2]) if len(log['topics']) > 2 else ZERO_ADDRESS
        amount = decode_uint256(log['data']) / TOKEN_DIVISOR

        transfer_type = 'transfer'
        if from_addr.lower() == ZERO_ADDRESS.lower():
            transfer_type = 'deposit'
        elif to_addr.lower() == ZERO_ADDRESS.lower():
            transfer_type = 'withdrawal'

        data.append({
            'timestamp': log['timestamp'],
            'block': log['block_number'],
            'tx_hash': log['tx_hash'],
            'from': from_addr,
            'to': to_addr,
            'amount': amount,
            'type': transfer_type,
        })

    df = pd.DataFrame(data)
    _cache[cache_key] = df
    return df


def get_pendle_swaps(days: int = 30) -> pd.DataFrame:
    """Get Pendle market swap events from all markets"""
    cache_key = f"pendle_swaps_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    from_block = get_block_by_timestamp(
        int((datetime.now() - timedelta(days=days)).timestamp())
    )

    all_logs = []
    for market_name, market_info in PENDLE_MARKETS.items():
        logs = fetch_logs(
            market_info['market'],
            [EVENTS['SWAP']],
            from_block
        )
        for log in logs:
            log['market'] = market_name
        all_logs.extend(logs)

    if not all_logs:
        return pd.DataFrame()

    all_logs = add_block_timestamps(all_logs)

    data = []
    for log in all_logs:
        caller = decode_address(log['topics'][1]) if len(log['topics']) > 1 else ZERO_ADDRESS
        receiver = decode_address(log['topics'][2]) if len(log['topics']) > 2 else ZERO_ADDRESS

        net_pt_out = decode_int256(log['data'], 0) / TOKEN_DIVISOR
        net_sy_out = decode_int256(log['data'], 1) / TOKEN_DIVISOR
        sy_fee = decode_uint256(log['data'], 2) / TOKEN_DIVISOR

        data.append({
            'timestamp': log['timestamp'],
            'block': log['block_number'],
            'tx_hash': log['tx_hash'],
            'market': log.get('market', 'unknown'),
            'caller': caller,
            'receiver': receiver,
            'net_pt_out': net_pt_out,
            'net_sy_out': net_sy_out,
            'fee': sy_fee,
            'volume': abs(net_sy_out),
        })

    df = pd.DataFrame(data)
    _cache[cache_key] = df
    return df


def get_pendle_lp_events(days: int = 30) -> pd.DataFrame:
    """Get Pendle LP mint/burn events from all markets"""
    cache_key = f"pendle_lp_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    from_block = get_block_by_timestamp(
        int((datetime.now() - timedelta(days=days)).timestamp())
    )

    all_logs = []
    for market_name, market_info in PENDLE_MARKETS.items():
        mint_logs = fetch_logs(market_info['market'], [EVENTS['MINT']], from_block)
        burn_logs = fetch_logs(market_info['market'], [EVENTS['BURN']], from_block)
        for log in mint_logs + burn_logs:
            log['market'] = market_name
        all_logs.extend(mint_logs + burn_logs)

    if not all_logs:
        return pd.DataFrame()

    all_logs = add_block_timestamps(all_logs)

    data = []
    for log in all_logs:
        is_mint = log['topics'][0] == EVENTS['MINT']
        user = decode_address(log['topics'][1]) if len(log['topics']) > 1 else ZERO_ADDRESS
        lp_amount = decode_uint256(log['data'], 0) / TOKEN_DIVISOR

        data.append({
            'timestamp': log['timestamp'],
            'block': log['block_number'],
            'tx_hash': log['tx_hash'],
            'market': log.get('market', 'unknown'),
            'user': user,
            'lp_amount': lp_amount,
            'action': 'mint' if is_mint else 'burn',
        })

    df = pd.DataFrame(data)
    _cache[cache_key] = df
    return df


def get_reward_claims(days: int = 30) -> pd.DataFrame:
    """Get reward claim events"""
    cache_key = f"rewards_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    from_block = get_block_by_timestamp(
        int((datetime.now() - timedelta(days=days)).timestamp())
    )

    logs = fetch_logs(CONTRACTS['PENDLE_MARKET'], [EVENTS['REDEEM_REWARDS']], from_block)

    if not logs:
        return pd.DataFrame()

    logs = add_block_timestamps(logs)

    data = []
    for log in logs:
        user = decode_address(log['topics'][1]) if len(log['topics']) > 1 else ZERO_ADDRESS
        data.append({
            'timestamp': log['timestamp'],
            'block': log['block_number'],
            'tx_hash': log['tx_hash'],
            'user': user,
        })

    df = pd.DataFrame(data)
    _cache[cache_key] = df
    return df


# ============================================================================
# AGGREGATION FUNCTIONS
# ============================================================================

def get_daily_pendle_deposits(days: int = 30) -> pd.DataFrame:
    """Aggregate daily Pendle deposits and withdrawals"""
    df = get_sy_transfers(days)
    if df.empty:
        return pd.DataFrame(columns=['date', 'deposits', 'withdrawals', 'net_flow'])

    df['date'] = pd.to_datetime(df['timestamp']).dt.date

    deposits = df[df['type'] == 'deposit'].groupby('date')['amount'].sum()
    withdrawals = df[df['type'] == 'withdrawal'].groupby('date')['amount'].sum()

    result = pd.DataFrame({
        'deposits': deposits,
        'withdrawals': withdrawals,
    }).fillna(0)

    result['net_flow'] = result['deposits'] - result['withdrawals']
    return result.reset_index()


def get_daily_volume(days: int = 30) -> pd.DataFrame:
    """Aggregate daily Pendle swap volume"""
    df = get_pendle_swaps(days)
    if df.empty:
        return pd.DataFrame(columns=['date', 'volume', 'fees', 'num_swaps', 'traders'])

    df['date'] = pd.to_datetime(df['timestamp']).dt.date

    result = df.groupby('date').agg({
        'volume': 'sum',
        'fee': 'sum',
        'tx_hash': 'count',
        'caller': 'nunique',
    }).rename(columns={
        'fee': 'fees',
        'tx_hash': 'num_swaps',
        'caller': 'traders',
    })

    return result.reset_index()


def get_nlp_tvl(days: int = 30) -> pd.DataFrame:
    """Calculate nLP TVL over time"""
    df = get_nlp_transfers(days)
    if df.empty:
        return pd.DataFrame(columns=['date', 'daily_change', 'tvl'])

    df['date'] = pd.to_datetime(df['timestamp']).dt.date

    mints = df[df['type'] == 'mint'].groupby('date')['amount'].sum()
    burns = df[df['type'] == 'burn'].groupby('date')['amount'].sum()

    daily_change = (mints.fillna(0) - burns.fillna(0)).reset_index()
    daily_change.columns = ['date', 'daily_change']
    daily_change = daily_change.sort_values('date')
    daily_change['tvl'] = daily_change['daily_change'].cumsum()

    return daily_change


def get_daily_nlp_volume(days: int = 30) -> pd.DataFrame:
    """Aggregate daily nLP transfer volume"""
    df = get_nlp_transfers(days)
    if df.empty:
        return pd.DataFrame(columns=['date', 'volume', 'num_transfers'])

    transfers = df[df['type'] == 'transfer'].copy()
    if transfers.empty:
        return pd.DataFrame(columns=['date', 'volume', 'num_transfers'])

    transfers['date'] = pd.to_datetime(transfers['timestamp']).dt.date

    result = transfers.groupby('date').agg({
        'amount': 'sum',
        'tx_hash': 'count',
    }).rename(columns={
        'amount': 'volume',
        'tx_hash': 'num_transfers',
    })

    return result.reset_index()


def get_top_holders(days: int = 90) -> pd.DataFrame:
    """Get current top nLP holders"""
    df = get_nlp_transfers(days)
    if df.empty:
        return pd.DataFrame(columns=['holder', 'balance', 'pct_supply'])

    received = df.groupby('to')['amount'].sum()
    sent = df.groupby('from')['amount'].sum()

    balances = (received.fillna(0) - sent.fillna(0)).reset_index()
    balances.columns = ['holder', 'balance']

    balances = balances[
        (balances['holder'].str.lower() != ZERO_ADDRESS.lower()) &
        (balances['balance'] > 0.01)
    ]

    total_supply = balances['balance'].sum()
    if total_supply > 0:
        balances['pct_supply'] = (balances['balance'] / total_supply * 100).round(2)
    else:
        balances['pct_supply'] = 0

    return balances.sort_values('balance', ascending=False).head(20)


def get_user_stats(days: int = 30) -> pd.DataFrame:
    """Get daily active users"""
    nlp_df = get_nlp_transfers(days)
    swap_df = get_pendle_swaps(days)

    users = []

    if not nlp_df.empty:
        nlp_df['date'] = pd.to_datetime(nlp_df['timestamp']).dt.date
        for _, row in nlp_df.iterrows():
            if row['from'].lower() != ZERO_ADDRESS.lower():
                users.append({'date': row['date'], 'user': row['from'].lower(), 'product': 'nLP'})
            if row['to'].lower() != ZERO_ADDRESS.lower():
                users.append({'date': row['date'], 'user': row['to'].lower(), 'product': 'nLP'})

    if not swap_df.empty:
        swap_df['date'] = pd.to_datetime(swap_df['timestamp']).dt.date
        for _, row in swap_df.iterrows():
            users.append({'date': row['date'], 'user': row['caller'].lower(), 'product': 'Pendle'})

    if not users:
        return pd.DataFrame(columns=['date', 'daily_users', 'nlp_users', 'pendle_users'])

    users_df = pd.DataFrame(users).drop_duplicates()

    result = users_df.groupby('date')['user'].nunique().reset_index()
    result.columns = ['date', 'daily_users']

    nlp_users = users_df[users_df['product'] == 'nLP'].groupby('date')['user'].nunique()
    pendle_users = users_df[users_df['product'] == 'Pendle'].groupby('date')['user'].nunique()

    result = result.set_index('date')
    result['nlp_users'] = nlp_users
    result['pendle_users'] = pendle_users
    result = result.fillna(0).astype({'nlp_users': int, 'pendle_users': int})

    return result.reset_index()


def get_kpi_summary(days: int = 30) -> Dict:
    """Get key performance indicators"""
    nlp_df = get_nlp_transfers(days)
    swap_df = get_pendle_swaps(days)
    sy_df = get_sy_transfers(days)

    # Calculate TVL
    if not nlp_df.empty:
        mints = nlp_df[nlp_df['type'] == 'mint']['amount'].sum()
        burns = nlp_df[nlp_df['type'] == 'burn']['amount'].sum()
        tvl = mints - burns
    else:
        tvl = 0
        mints = 0
        burns = 0

    # nLP Volume = total deposits + withdrawals (mints + burns)
    nlp_volume = mints + burns if not nlp_df.empty else 0

    # Calculate swap volume (7d)
    if not swap_df.empty:
        seven_days_ago = datetime.now() - timedelta(days=7)
        swap_df['timestamp'] = pd.to_datetime(swap_df['timestamp'])
        recent_swaps = swap_df[swap_df['timestamp'] >= seven_days_ago]
        swap_volume_7d = recent_swaps['volume'].sum() if not recent_swaps.empty else 0
        total_swap_volume = swap_df['volume'].sum()
        total_fees = swap_df['fee'].sum()
    else:
        swap_volume_7d = 0
        total_swap_volume = 0
        total_fees = 0

    # Pendle deposits/withdrawals
    if not sy_df.empty:
        pendle_deposits = sy_df[sy_df['type'] == 'deposit']['amount'].sum()
        pendle_withdrawals = sy_df[sy_df['type'] == 'withdrawal']['amount'].sum()
    else:
        pendle_deposits = 0
        pendle_withdrawals = 0

    # Total Pendle Volume = swap volume + deposits + withdrawals
    pendle_total_volume = total_swap_volume + pendle_deposits + pendle_withdrawals

    # Count users
    all_users = set()
    if not nlp_df.empty:
        all_users.update(nlp_df['from'].str.lower().tolist())
        all_users.update(nlp_df['to'].str.lower().tolist())
    if not swap_df.empty:
        all_users.update(swap_df['caller'].str.lower().tolist())
    all_users.discard(ZERO_ADDRESS.lower())

    return {
        'tvl': round(tvl, 2),
        'nlp_volume': round(nlp_volume, 2),
        'swap_volume_7d': round(swap_volume_7d, 2),
        'pendle_total_volume': round(pendle_total_volume, 2),
        'pendle_deposits': round(pendle_deposits, 2),
        'pendle_withdrawals': round(pendle_withdrawals, 2),
        'total_fees': round(total_fees, 4),
        'total_users': len(all_users),
    }


def get_market_stats(days: int = 30) -> Dict:
    """Get stats per Pendle market"""
    swap_df = get_pendle_swaps(days)
    lp_df = get_pendle_lp_events(days)

    market_stats = {}

    for market_name in PENDLE_MARKETS.keys():
        # Swap stats for this market
        if not swap_df.empty:
            market_swaps = swap_df[swap_df['market'] == market_name]
            swap_volume = market_swaps['volume'].sum() if not market_swaps.empty else 0
            swap_count = len(market_swaps)
            fees = market_swaps['fee'].sum() if not market_swaps.empty else 0
        else:
            swap_volume = 0
            swap_count = 0
            fees = 0

        # LP stats for this market
        if not lp_df.empty:
            market_lp = lp_df[lp_df['market'] == market_name]
            mints = market_lp[market_lp['action'] == 'mint']['lp_amount'].sum() if not market_lp.empty else 0
            burns = market_lp[market_lp['action'] == 'burn']['lp_amount'].sum() if not market_lp.empty else 0
        else:
            mints = 0
            burns = 0

        market_stats[market_name] = {
            'swap_volume': round(swap_volume, 2),
            'swap_count': swap_count,
            'fees': round(fees, 4),
            'lp_mints': round(mints, 2),
            'lp_burns': round(burns, 2),
            'net_lp': round(mints - burns, 2),
        }

    return market_stats


def get_total_supply(contract_address: str, decimals: int = TOKEN_DECIMALS) -> float:
    """Get total supply of a token (instant, accurate TVL)"""
    # totalSupply() selector: 0x18160ddd
    result = rpc_call("eth_call", [{"to": contract_address, "data": "0x18160ddd"}, "latest"])
    if result:
        return int(result, 16) / (10 ** decimals)
    return 0


def get_accurate_tvl() -> Dict:
    """Get accurate TVL using totalSupply() - instant and accurate"""
    cache_key = "accurate_tvl"
    if cache_key in _cache:
        return _cache[cache_key]

    wNLP_supply = get_total_supply(CONTRACTS['wNLP'], decimals=6)
    SY_supply = get_total_supply(CONTRACTS['SY_wNLP'], decimals=6)
    nHYPE_supply = get_total_supply(CONTRACTS['nHYPE'], decimals=18)

    result = {
        'wNLP_tvl': round(wNLP_supply, 2),
        'SY_tvl': round(SY_supply, 2),
        'nHYPE_tvl': round(nHYPE_supply, 2),
    }

    _cache[cache_key] = result
    return result


def load_alltime_cache() -> Dict:
    """Load all-time totals from disk cache"""
    if os.path.exists(ALLTIME_CACHE_FILE):
        try:
            with open(ALLTIME_CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_alltime_cache(data: Dict):
    """Save all-time totals to disk cache"""
    try:
        with open(ALLTIME_CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Failed to save cache: {e}")


def fetch_alltime_totals(contract: str, start_block: int, progress_callback=None) -> Dict:
    """Fetch all-time transfer totals for a contract"""
    current_block = get_current_block()
    if current_block == 0:
        return {'mints': 0, 'burns': 0, 'transfers': 0, 'last_block': 0}

    total_mints = 0
    total_burns = 0
    total_transfers = 0
    batch_size = 900
    current_from = start_block

    while current_from <= current_block:
        current_to = min(current_from + batch_size, current_block)

        params = [{
            "fromBlock": hex(current_from),
            "toBlock": hex(current_to),
            "address": contract,
            "topics": [EVENTS['TRANSFER']],
        }]

        result = rpc_call("eth_getLogs", params)

        if isinstance(result, list):
            for log in result:
                from_addr = '0x' + log['topics'][1][-40:] if len(log['topics']) > 1 else ZERO_ADDRESS
                to_addr = '0x' + log['topics'][2][-40:] if len(log['topics']) > 2 else ZERO_ADDRESS
                data = log.get('data', '0x')
                amount = int(data, 16) / TOKEN_DIVISOR if data and data != '0x' else 0

                if from_addr.lower() == ZERO_ADDRESS.lower():
                    total_mints += amount
                elif to_addr.lower() == ZERO_ADDRESS.lower():
                    total_burns += amount
                else:
                    total_transfers += amount

        if progress_callback:
            progress = (current_from - start_block) / (current_block - start_block)
            progress_callback(progress)

        time.sleep(0.05)  # Rate limiting
        current_from = current_to + 1

    return {
        'mints': round(total_mints, 2),
        'burns': round(total_burns, 2),
        'transfers': round(total_transfers, 2),
        'last_block': current_block,
    }


def get_alltime_totals(force_refresh: bool = False) -> Dict:
    """Get all-time totals from cache or fetch if needed"""
    cache = load_alltime_cache()

    current_block = get_current_block()

    # Check if we need to update (cache is empty or stale by >10000 blocks)
    needs_update = {}
    for name, contract in [('wNLP', CONTRACTS['wNLP']), ('SY_wNLP', CONTRACTS['SY_wNLP'])]:
        if force_refresh or name not in cache:
            needs_update[name] = CONTRACT_START_BLOCKS.get(name, 20000000)
        elif current_block - cache[name].get('last_block', 0) > 10000:
            # Just fetch from last block instead of from beginning
            needs_update[name] = cache[name].get('last_block', CONTRACT_START_BLOCKS.get(name, 20000000))

    # Return cached data if no update needed
    if not needs_update and cache:
        return cache

    # Fetch missing/stale data
    for name, start_block in needs_update.items():
        contract = CONTRACTS['wNLP'] if name == 'wNLP' else CONTRACTS['SY_wNLP']
        print(f"Fetching all-time data for {name} from block {start_block}...")

        new_data = fetch_alltime_totals(contract, start_block)

        if name in cache:
            # Add to existing totals
            cache[name]['mints'] = round(cache[name].get('mints', 0) + new_data['mints'], 2)
            cache[name]['burns'] = round(cache[name].get('burns', 0) + new_data['burns'], 2)
            cache[name]['transfers'] = round(cache[name].get('transfers', 0) + new_data['transfers'], 2)
            cache[name]['last_block'] = new_data['last_block']
        else:
            cache[name] = new_data

    save_alltime_cache(cache)
    return cache


def get_apy_history(days: int = 7) -> pd.DataFrame:
    """Fetch historical APY data from Pendle API"""
    cache_key = f"apy_history_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    all_data = []
    for market_name, market_info in PENDLE_MARKETS.items():
        try:
            response = requests.get(
                f"https://api-v2.pendle.finance/core/v1/999/markets/{market_info['market']}/apy-history",
                timeout=15
            )
            data = response.json()

            for entry in data.get('results', []):
                all_data.append({
                    'timestamp': pd.to_datetime(entry['timestamp']),
                    'market': market_name,
                    'underlying_apy': entry.get('underlyingApy', 0) * 100,
                    'implied_apy': entry.get('impliedApy', 0) * 100,
                })
        except Exception as e:
            print(f"Failed to fetch APY history for {market_name}: {e}")

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    # Filter to requested days - convert timestamp to naive datetime for comparison
    cutoff = datetime.now() - timedelta(days=days)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    df = df[df['timestamp'] >= cutoff]

    _cache[cache_key] = df
    return df


def get_pendle_apy() -> Dict:
    """Fetch APY data from Pendle API"""
    cache_key = "pendle_apy"
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        response = requests.get(
            "https://api-v2.pendle.finance/core/v1/999/markets",
            timeout=10
        )
        data = response.json()

        apy_data = {}
        for market in data.get('results', []):
            name = market.get('proName', market.get('name', ''))
            if 'wNLP' in name or 'nLP' in name.lower():
                addr = market.get('address', '').lower()
                underlying_apy = market.get('underlyingInterestApy', 0) * 100
                tvl_usd = market.get('liquidity', {}).get('usd', 0)

                # Calculate distributed yield (APY × TVL)
                daily_yield = (underlying_apy / 100 / 365) * tvl_usd
                weekly_yield = daily_yield * 7
                monthly_yield = daily_yield * 30
                annual_yield = (underlying_apy / 100) * tvl_usd

                apy_data[addr] = {
                    'name': name,
                    'implied_apy': round(market.get('impliedApy', 0) * 100, 2),
                    'underlying_apy': round(underlying_apy, 2),
                    'tvl_usd': round(tvl_usd, 2),
                    'pt_price': market.get('pt', {}).get('price', {}).get('usd', 0),
                    'yt_price': market.get('yt', {}).get('price', {}).get('usd', 0),
                    'expiry': market.get('expiry', ''),
                    # Distributed yield calculations
                    'daily_yield': round(daily_yield, 2),
                    'weekly_yield': round(weekly_yield, 2),
                    'monthly_yield': round(monthly_yield, 2),
                    'annual_yield': round(annual_yield, 2),
                }

        _cache[cache_key] = apy_data
        return apy_data
    except Exception as e:
        print(f"Failed to fetch Pendle APY: {e}")
        return {}


def clear_cache():
    """Clear all cached data"""
    _cache.clear()


# ============================================================================
# HYPERSCAN API FUNCTIONS (for efficient all-time data fetching)
# ============================================================================

HYPERSCAN_API = "https://www.hyperscan.com/api/v2"


def fetch_all_token_transfers_hyperscan(token_address: str) -> Dict:
    """
    Fetch all transfers of a token from Hyperscan API.
    Returns totals for mints, burns, and regular transfers.
    """
    url = f"{HYPERSCAN_API}/tokens/{token_address}/transfers"

    all_transfers = []
    next_params = None
    page = 0

    print(f"Fetching transfers for {token_address[:10]}... via Hyperscan API")

    while True:
        page += 1
        params = next_params or {}

        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                print(f"  Error on page {page}: {resp.status_code}")
                break

            data = resp.json()
            items = data.get('items', [])
            all_transfers.extend(items)

            if page % 20 == 0:
                print(f"  Page {page}: {len(all_transfers)} transfers...")

            next_params = data.get('next_page_params')
            if not next_params:
                break

            time.sleep(0.1)  # Rate limiting

        except Exception as e:
            print(f"  Request failed: {e}")
            break

    print(f"  Total transfers: {len(all_transfers)}")

    # Calculate totals and track unique users
    mints = 0.0
    burns = 0.0
    transfers = 0.0
    unique_users = set()

    for tx in all_transfers:
        from_addr = tx.get('from', {}).get('hash', '').lower()
        to_addr = tx.get('to', {}).get('hash', '').lower()
        value = int(tx.get('total', {}).get('value', '0'))
        decimals = int(tx.get('total', {}).get('decimals', '6') or '6')
        amount = value / (10 ** decimals)

        # Track unique users (exclude zero address)
        if from_addr != ZERO_ADDRESS.lower():
            unique_users.add(from_addr)
        if to_addr != ZERO_ADDRESS.lower():
            unique_users.add(to_addr)

        if from_addr == ZERO_ADDRESS.lower():
            mints += amount
        elif to_addr == ZERO_ADDRESS.lower():
            burns += amount
        else:
            transfers += amount

    return {
        'mints': round(mints, 2),
        'burns': round(burns, 2),
        'transfers': round(transfers, 2),
        'total_count': len(all_transfers),
        'unique_users': len(unique_users),
        'user_addresses': unique_users,  # Keep for deduplication across tokens
    }


def get_alltime_totals_hyperscan(force_refresh: bool = False) -> Dict:
    """
    Get all-time totals using Hyperscan API (much faster than RPC).
    Returns cached data if available, otherwise fetches from API.
    """
    cache_key = "alltime_hyperscan"

    # Check memory cache first
    if not force_refresh and cache_key in _cache:
        return _cache[cache_key]

    # Check disk cache
    cache = load_alltime_cache()
    if not force_refresh and 'hyperscan' in cache:
        _cache[cache_key] = cache['hyperscan']
        return cache['hyperscan']

    # Fetch from Hyperscan API
    print("Fetching all-time totals from Hyperscan API...")

    wNLP_data = fetch_all_token_transfers_hyperscan(CONTRACTS['wNLP'])
    SY_data = fetch_all_token_transfers_hyperscan(CONTRACTS['SY_wNLP'])

    # Combine unique users from both tokens (deduplicated)
    all_users = wNLP_data['user_addresses'] | SY_data['user_addresses']

    result = {
        'wNLP': {
            'deposits': wNLP_data['mints'],
            'withdrawals': wNLP_data['burns'],
            'volume': wNLP_data['mints'] + wNLP_data['burns'],
            'transfers': wNLP_data['transfers'],
            'transfer_count': wNLP_data['total_count'],
            'unique_users': wNLP_data['unique_users'],
        },
        'SY_wNLP': {
            'deposits': SY_data['mints'],
            'withdrawals': SY_data['burns'],
            'volume': SY_data['mints'] + SY_data['burns'],
            'transfers': SY_data['transfers'],
            'transfer_count': SY_data['total_count'],
            'unique_users': SY_data['unique_users'],
        },
        'total_unique_users': len(all_users),
        'timestamp': datetime.now().isoformat(),
    }

    # Save to disk cache
    cache['hyperscan'] = result
    save_alltime_cache(cache)

    # Save to memory cache
    _cache[cache_key] = result

    return result


def fetch_pendle_market_logs_hyperscan(market_address: str, market_name: str) -> Dict:
    """
    Fetch all logs for a Pendle market contract via Hyperscan API.
    Returns swap counts and volume estimates.
    """
    url = f"{HYPERSCAN_API}/addresses/{market_address}/logs"

    all_logs = []
    next_params = None
    page = 0

    print(f"Fetching logs for {market_name} ({market_address[:10]}...)...")

    while True:
        page += 1
        params = next_params or {}

        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                print(f"  Error on page {page}: {resp.status_code}")
                break

            data = resp.json()
            items = data.get('items', [])
            all_logs.extend(items)

            if page % 20 == 0:
                print(f"  Page {page}: {len(all_logs)} logs...")

            next_params = data.get('next_page_params')
            if not next_params:
                break

            time.sleep(0.1)

        except Exception as e:
            print(f"  Request failed: {e}")
            break

    print(f"  Total logs: {len(all_logs)}")

    # Count events by topic (Swap, Mint, Burn)
    SWAP_TOPIC = EVENTS['SWAP'].lower()
    MINT_TOPIC = EVENTS['MINT'].lower()
    BURN_TOPIC = EVENTS['BURN'].lower()

    swap_count = 0
    mint_count = 0
    burn_count = 0
    unique_users = set()

    for log in all_logs:
        # Topics is an array - first element is the event signature
        topics = log.get('topics', [])
        topic = (topics[0] or '').lower() if topics and topics[0] else ''

        # Try to get transaction sender from indexed parameters
        if len(topics) > 1 and topics[1]:
            # Second topic is usually the 'from' or 'caller' address
            topic1 = topics[1] or ''
            if len(topic1) >= 40:
                addr = '0x' + topic1[-40:]
                if addr.lower() != ZERO_ADDRESS.lower():
                    unique_users.add(addr.lower())

        if topic == SWAP_TOPIC:
            swap_count += 1
        elif topic == MINT_TOPIC:
            mint_count += 1
        elif topic == BURN_TOPIC:
            burn_count += 1

    return {
        'swap_count': swap_count,
        'mint_count': mint_count,
        'burn_count': burn_count,
        'total_logs': len(all_logs),
        'unique_users': len(unique_users),
    }


def get_alltime_pendle_markets_hyperscan(force_refresh: bool = False) -> Dict:
    """
    Get all-time stats for both Pendle markets via Hyperscan API.
    """
    cache_key = "alltime_pendle_markets"

    if not force_refresh and cache_key in _cache:
        return _cache[cache_key]

    cache = load_alltime_cache()
    if not force_refresh and 'pendle_markets' in cache:
        _cache[cache_key] = cache['pendle_markets']
        return cache['pendle_markets']

    print("Fetching all-time Pendle market stats from Hyperscan API...")

    result = {}
    for market_name, market_info in PENDLE_MARKETS.items():
        data = fetch_pendle_market_logs_hyperscan(market_info['market'], market_name)
        result[market_name] = {
            'market_address': market_info['market'],
            'expiry': market_info['expiry'],
            'swap_count': data['swap_count'],
            'mint_count': data['mint_count'],
            'burn_count': data['burn_count'],
            'total_events': data['total_logs'],
            'unique_users': data['unique_users'],
        }

    result['timestamp'] = datetime.now().isoformat()

    cache['pendle_markets'] = result
    save_alltime_cache(cache)
    _cache[cache_key] = result

    return result


def fetch_market_peak_tvl(market_address: str) -> Dict:
    """
    Calculate peak TVL for a Pendle market by analyzing SY token transfers.
    Returns peak_tvl, peak_date, and current_balance.
    """
    SY_TOKEN = CONTRACTS['SY_wNLP']

    url = f"{HYPERSCAN_API}/addresses/{market_address}/token-transfers"
    params = {"token": SY_TOKEN, "type": "ERC-20"}

    all_transfers = []
    page = 0

    while True:
        page += 1
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                break
            data = resp.json()
            items = data.get('items', [])
            all_transfers.extend(items)

            next_params = data.get('next_page_params')
            if not next_params:
                break
            params = next_params
            params["token"] = SY_TOKEN
            params["type"] = "ERC-20"
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching transfers: {e}")
            break

    if not all_transfers:
        return {'peak_tvl': 0, 'peak_date': None, 'current_balance': 0}

    # Sort by timestamp (oldest first)
    all_transfers.sort(key=lambda x: x['timestamp'])

    # Calculate running balance
    balance = 0
    peak_balance = 0
    peak_date = None
    market_lower = market_address.lower()

    for t in all_transfers:
        from_addr = t['from']['hash'].lower()
        to_addr = t['to']['hash'].lower()
        value = int(t['total']['value']) / (10 ** TOKEN_DECIMALS)
        ts = t['timestamp']

        if to_addr == market_lower:
            balance += value
        elif from_addr == market_lower:
            balance -= value

        if balance > peak_balance:
            peak_balance = balance
            peak_date = ts

    return {
        'peak_tvl': round(peak_balance, 2),
        'peak_date': peak_date,
        'current_balance': round(balance, 2)
    }


def get_pendle_peak_tvls(force_refresh: bool = False) -> Dict:
    """
    Get peak TVL data for all Pendle markets.
    """
    cache_key = "pendle_peak_tvls"

    if not force_refresh and cache_key in _cache:
        return _cache[cache_key]

    cache = load_alltime_cache()
    if not force_refresh and 'pendle_peak_tvls' in cache:
        _cache[cache_key] = cache['pendle_peak_tvls']
        return cache['pendle_peak_tvls']

    print("Fetching peak TVL data for Pendle markets...")

    result = {}
    for market_name, market_info in PENDLE_MARKETS.items():
        print(f"  Processing {market_name}...")
        tvl_data = fetch_market_peak_tvl(market_info['market'])
        result[market_name] = tvl_data

    result['timestamp'] = datetime.now().isoformat()

    cache['pendle_peak_tvls'] = result
    save_alltime_cache(cache)
    _cache[cache_key] = result

    return result


# ============================================================================
# HYPERLIQUID HIP-3 VOLUME DATA
# ============================================================================

HYPERLIQUID_TESTNET_API = "https://api.hyperliquid-testnet.xyz/info"

HIP3_PAIRS = ["nunchi:VXX", "nunchi:US3M"]


def fetch_hip3_volume(coin: str) -> Dict:
    """
    Fetch all-time volume for a HIP-3 pair from daily candles.
    Returns base volume and notional volume (USD).
    """
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": "1d",
            "startTime": 0,
            "endTime": 9999999999999
        }
    }

    try:
        resp = requests.post(HYPERLIQUID_TESTNET_API, json=payload, timeout=30)
        data = resp.json()

        if not isinstance(data, list):
            return {'base_volume': 0, 'notional_volume': 0, 'days': 0}

        total_base_vol = 0
        total_notional_vol = 0

        for candle in data:
            base_vol = float(candle.get('v', 0))
            o = float(candle.get('o', 0))
            c = float(candle.get('c', 0))
            avg_px = (o + c) / 2 if (o + c) > 0 else 0

            total_base_vol += base_vol
            total_notional_vol += base_vol * avg_px

        return {
            'base_volume': round(total_base_vol, 2),
            'notional_volume': round(total_notional_vol, 2),
            'days': len(data)
        }
    except Exception as e:
        print(f"Error fetching HIP-3 volume for {coin}: {e}")
        return {'base_volume': 0, 'notional_volume': 0, 'days': 0}


def get_hip3_volumes() -> Dict:
    """
    Get all-time volume data for Nunchi HIP-3 pairs on Hyperliquid testnet.
    """
    cache_key = "hip3_volumes"

    if cache_key in _cache:
        return _cache[cache_key]

    result = {}
    total_notional = 0

    for pair in HIP3_PAIRS:
        vol_data = fetch_hip3_volume(pair)
        result[pair] = vol_data
        total_notional += vol_data['notional_volume']

    result['total_notional'] = round(total_notional, 2)
    result['timestamp'] = datetime.now().isoformat()

    _cache[cache_key] = result
    return result


# ============================================================================
# TESTNET ANALYTICS API
# ============================================================================

TESTNET_ANALYTICS_API = "https://api-temp.nunchi.trade/api/v1/analytics"

# Asset mapping for Season One (no asset field in API)
SEASON_ONE_ASSET_MAP = {
    "0xe83eE565057FA5e19e0796B3ED0c3f5218Dc810f": "BTC_FR",
    "0x892D876376bD643e4D71CA4c4030aA4d9D61Ff9c": "ETH_FR",
    "0x29944a5e8965A108a75027D4d8B84C1FE5a9AC58": "HYPE_FR",
    "0x4B77aB49cF251bb1Ed0419118c632ba71Bc520e3": "SOL_FR",
    "0x921e8b52f688e531287e28d72cB0bCA1c8f4f09B": "stETH_ETH",
    "0x18951e3867Fb328eFA012AAfF5E1E1275d1E7256": "VXX",
    "0x84e4F3A30FA4414A9A0212836C6d5ca2dFf9342d": "MSTY",
    "0x37725df43f82CB25184Dfabe7530C9AB42307aA8": "XYZ100_FR",
    "0xEef584DD7fff7a497F891E19C95d351c8b345Cc9": "VXX",
    "0xF148Abde8fe45d0d753Dbb9e3eb69521Ea6F26E2": "MSTY",
    "0x6e1c1275D49b4B09EAc99b0339004A4FDBd30cD8": "TBILL",
    "0xb70eD964b5ea4fE718F9BA445ebCac98F73A3A67": "HYPE_FR",
}

CHAIN_NAMES = {
    6342: "MegaETH",
    10143: "Monad",
}


def get_testnet_analytics() -> Dict:
    """
    Fetch testnet analytics from Nunchi API.
    Returns simulator, season one, and season two data.
    """
    cache_key = "testnet_analytics"

    if cache_key in _cache:
        return _cache[cache_key]

    try:
        resp = requests.get(TESTNET_ANALYTICS_API, timeout=30)
        data = resp.json()

        # Process the data
        result = {
            'simulator': process_simulator_data(data.get('simulator', {})),
            'season_one': process_season_one_data(data.get('seasonOne', {})),
            'season_two': process_season_two_data(data.get('seasonTwo', {})),
            'timestamp': datetime.now().isoformat(),
        }

        # Calculate totals
        result['totals'] = {
            'total_users': (
                result['simulator']['total_users'] +
                result['season_one']['total']['total_users'] +
                result['season_two']['total']['total_users']
            ),
            'total_volume': (
                result['simulator']['total_volume'] +
                result['season_one']['total']['total_volume'] +
                result['season_two']['total']['total_volume']
            ),
        }

        _cache[cache_key] = result
        return result

    except Exception as e:
        print(f"Error fetching testnet analytics: {e}")
        return {}


def process_simulator_data(data: Dict) -> Dict:
    """Process simulator data from API."""
    return {
        'total_users': data.get('totalUsers', 0),
        'total_volume': data.get('totalVolume', 0) * 100,  # API returns in different scale
        'avg_volume_per_user': data.get('averageVolumePerUser', 0),
    }


def parse_time_string(time_str: str) -> float:
    """
    Parse time string format "HH:MM:SS:ms" to total hours.
    Returns 0 if invalid or zero time.
    """
    if not time_str or time_str == "00:00:00:000":
        return 0
    try:
        parts = time_str.split(':')
        if len(parts) >= 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2]) if len(parts) == 3 else int(parts[2])
            # Convert to total hours
            return hours + minutes / 60 + seconds / 3600
    except:
        pass
    return 0


def format_hours_to_readable(hours: float) -> str:
    """Convert hours to readable format like '5d 12h' or '2h 30m'."""
    if hours <= 0:
        return "N/A"

    days = int(hours // 24)
    remaining_hours = int(hours % 24)

    if days > 0:
        return f"{days}d {remaining_hours}h"
    elif hours >= 1:
        minutes = int((hours % 1) * 60)
        return f"{int(hours)}h {minutes}m"
    else:
        minutes = int(hours * 60)
        return f"{minutes}m"


def process_season_one_data(data: Dict) -> Dict:
    """Process Season One data with asset mapping."""
    by_contract = data.get('byContract', [])
    by_chain = data.get('byChain', {})
    total = data.get('total', {})

    # Map assets to contracts and collect net profit / time data
    contracts_with_assets = []
    total_net_profit = 0
    total_time_to_close_hours = 0
    contracts_with_close_time = 0

    for contract in by_contract:
        addr = contract.get('contractAddress', '')
        asset = SEASON_ONE_ASSET_MAP.get(addr, 'Unknown')
        net_profit = contract.get('netProfit', 0)
        avg_time_close = contract.get('avgTimeToClose', '00:00:00:000')
        time_hours = parse_time_string(avg_time_close)

        total_net_profit += net_profit
        if time_hours > 0:
            total_time_to_close_hours += time_hours
            contracts_with_close_time += 1

        contracts_with_assets.append({
            'contract': addr,
            'chain': contract.get('chain'),
            'chain_name': CHAIN_NAMES.get(contract.get('chain'), 'Unknown'),
            'asset': asset,
            'users': contract.get('totalUsers', 0),
            'volume': contract.get('totalVolume', 0),
            'avg_per_user': contract.get('averageVolumePerUser', 0),
            'net_profit': net_profit,
            'avg_time_to_close': time_hours,
        })

    # Aggregate by asset
    by_asset = {}
    for c in contracts_with_assets:
        asset = c['asset']
        if asset not in by_asset:
            by_asset[asset] = {'users': 0, 'volume': 0, 'net_profit': 0}
        by_asset[asset]['users'] += c['users']
        by_asset[asset]['volume'] += c['volume']
        by_asset[asset]['net_profit'] += c['net_profit']

    # Process by chain
    chains = {}
    for chain_id, chain_data in by_chain.items():
        chains[int(chain_id)] = {
            'name': CHAIN_NAMES.get(int(chain_id), 'Unknown'),
            'users': chain_data.get('totalUsers', 0),
            'volume': chain_data.get('totalVolume', 0),
            'avg_per_user': chain_data.get('averageVolumePerUser', 0),
        }

    # Calculate average time to close
    avg_time_to_close = total_time_to_close_hours / contracts_with_close_time if contracts_with_close_time > 0 else 0

    return {
        'by_contract': contracts_with_assets,
        'by_asset': by_asset,
        'by_chain': chains,
        'total': {
            'total_users': total.get('totalUsers', 0),
            'total_volume': total.get('totalVolume', 0),
            'avg_per_user': total.get('averageVolumePerUser', 0),
            'net_profit': total_net_profit,
            'avg_time_to_close_hours': avg_time_to_close,
            'avg_time_to_close_formatted': format_hours_to_readable(avg_time_to_close),
        }
    }


def process_season_two_data(data: Dict) -> Dict:
    """Process Season Two data."""
    by_contract = data.get('byContract', [])
    by_asset = data.get('byAsset', {})
    by_chain = data.get('byChain', {})
    total = data.get('total', {})

    # Process contracts and collect net profit / time data
    contracts = []
    total_net_profit = 0
    total_time_to_close_hours = 0
    contracts_with_close_time = 0

    for contract in by_contract:
        net_profit = contract.get('netProfit', 0)
        avg_time_close = contract.get('avgTimeToClose', '00:00:00:000')
        time_hours = parse_time_string(avg_time_close)

        total_net_profit += net_profit
        if time_hours > 0:
            total_time_to_close_hours += time_hours
            contracts_with_close_time += 1

        contracts.append({
            'contract': contract.get('contractAddress', ''),
            'chain': contract.get('chain'),
            'chain_name': CHAIN_NAMES.get(contract.get('chain'), 'Unknown'),
            'asset': contract.get('asset', 'Unknown'),
            'users': contract.get('totalUsers', 0),
            'volume': contract.get('totalVolume', 0),
            'avg_per_user': contract.get('averageVolumePerUser', 0),
            'net_profit': net_profit,
            'avg_time_to_close': time_hours,
        })

    # Aggregate net profit by asset from contracts
    asset_profits = {}
    for c in contracts:
        asset = c['asset']
        if asset not in asset_profits:
            asset_profits[asset] = 0
        asset_profits[asset] += c['net_profit']

    # Process assets
    assets = {}
    for asset_name, asset_data in by_asset.items():
        assets[asset_name] = {
            'users': asset_data.get('totalUsers', 0),
            'volume': asset_data.get('totalVolume', 0),
            'avg_per_user': asset_data.get('averageVolumePerUser', 0),
            'net_profit': asset_profits.get(asset_name, 0),
        }

    # Process chains
    chains = {}
    for chain_id, chain_data in by_chain.items():
        chains[int(chain_id)] = {
            'name': CHAIN_NAMES.get(int(chain_id), 'Unknown'),
            'users': chain_data.get('totalUsers', 0),
            'volume': chain_data.get('totalVolume', 0),
            'avg_per_user': chain_data.get('averageVolumePerUser', 0),
        }

    # Calculate average time to close
    avg_time_to_close = total_time_to_close_hours / contracts_with_close_time if contracts_with_close_time > 0 else 0

    return {
        'by_contract': contracts,
        'by_asset': assets,
        'by_chain': chains,
        'total': {
            'total_users': total.get('totalUsers', 0),
            'total_volume': total.get('totalVolume', 0),
            'avg_per_user': total.get('averageVolumePerUser', 0),
            'net_profit': total_net_profit,
            'avg_time_to_close_hours': avg_time_to_close,
            'avg_time_to_close_formatted': format_hours_to_readable(avg_time_to_close),
        }
    }


def get_season_comparison() -> Dict:
    """Get comparison data between seasons."""
    analytics = get_testnet_analytics()
    if not analytics:
        return {}

    s1_assets = analytics.get('season_one', {}).get('by_asset', {})
    s2_assets = analytics.get('season_two', {}).get('by_asset', {})

    # Get all unique assets
    all_assets = set(s1_assets.keys()) | set(s2_assets.keys())

    comparison = []
    for asset in sorted(all_assets):
        s1 = s1_assets.get(asset, {'users': 0, 'volume': 0})
        s2 = s2_assets.get(asset, {'users': 0, 'volume': 0})

        user_growth = ((s2['users'] - s1['users']) / s1['users'] * 100) if s1['users'] > 0 else 0
        vol_growth = ((s2['volume'] - s1['volume']) / s1['volume'] * 100) if s1['volume'] > 0 else 0

        comparison.append({
            'asset': asset,
            's1_users': s1['users'],
            's1_volume': s1['volume'],
            's2_users': s2['users'],
            's2_volume': s2['volume'],
            'user_growth': user_growth,
            'volume_growth': vol_growth,
        })

    return comparison
