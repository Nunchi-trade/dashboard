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

from config import (
    RPC_URL, CONTRACTS, EVENTS, ZERO_ADDRESS, CACHE_TTL
)

# Cache for expensive queries
_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)


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
        amount = decode_uint256(log['data']) / 1e18

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
        amount = decode_uint256(log['data']) / 1e18

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
    """Get Pendle market swap events"""
    cache_key = f"pendle_swaps_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    from_block = get_block_by_timestamp(
        int((datetime.now() - timedelta(days=days)).timestamp())
    )

    logs = fetch_logs(
        CONTRACTS['PENDLE_MARKET'],
        [EVENTS['SWAP']],
        from_block
    )

    if not logs:
        return pd.DataFrame()

    logs = add_block_timestamps(logs)

    data = []
    for log in logs:
        caller = decode_address(log['topics'][1]) if len(log['topics']) > 1 else ZERO_ADDRESS
        receiver = decode_address(log['topics'][2]) if len(log['topics']) > 2 else ZERO_ADDRESS

        net_pt_out = decode_int256(log['data'], 0) / 1e18
        net_sy_out = decode_int256(log['data'], 1) / 1e18
        sy_fee = decode_uint256(log['data'], 2) / 1e18

        data.append({
            'timestamp': log['timestamp'],
            'block': log['block_number'],
            'tx_hash': log['tx_hash'],
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
    """Get Pendle LP mint/burn events"""
    cache_key = f"pendle_lp_{days}"
    if cache_key in _cache:
        return _cache[cache_key]

    from_block = get_block_by_timestamp(
        int((datetime.now() - timedelta(days=days)).timestamp())
    )

    mint_logs = fetch_logs(CONTRACTS['PENDLE_MARKET'], [EVENTS['MINT']], from_block)
    burn_logs = fetch_logs(CONTRACTS['PENDLE_MARKET'], [EVENTS['BURN']], from_block)

    all_logs = mint_logs + burn_logs
    if not all_logs:
        return pd.DataFrame()

    all_logs = add_block_timestamps(all_logs)

    data = []
    for log in all_logs:
        is_mint = log['topics'][0] == EVENTS['MINT']
        user = decode_address(log['topics'][1]) if len(log['topics']) > 1 else ZERO_ADDRESS
        lp_amount = decode_uint256(log['data'], 0) / 1e18

        data.append({
            'timestamp': log['timestamp'],
            'block': log['block_number'],
            'tx_hash': log['tx_hash'],
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

    # Calculate volume (7d)
    if not swap_df.empty:
        seven_days_ago = datetime.now() - timedelta(days=7)
        swap_df['timestamp'] = pd.to_datetime(swap_df['timestamp'])
        recent_swaps = swap_df[swap_df['timestamp'] >= seven_days_ago]
        volume_7d = recent_swaps['volume'].sum() if not recent_swaps.empty else 0
        total_fees = swap_df['fee'].sum()
    else:
        volume_7d = 0
        total_fees = 0

    # Count users
    all_users = set()
    if not nlp_df.empty:
        all_users.update(nlp_df['from'].str.lower().tolist())
        all_users.update(nlp_df['to'].str.lower().tolist())
    if not swap_df.empty:
        all_users.update(swap_df['caller'].str.lower().tolist())
    all_users.discard(ZERO_ADDRESS.lower())

    # Pendle deposits
    if not sy_df.empty:
        pendle_deposits = sy_df[sy_df['type'] == 'deposit']['amount'].sum()
    else:
        pendle_deposits = 0

    return {
        'tvl': round(tvl, 2),
        'volume_7d': round(volume_7d, 2),
        'total_fees': round(total_fees, 4),
        'total_users': len(all_users),
        'pendle_deposits': round(pendle_deposits, 2),
    }


def clear_cache():
    """Clear all cached data"""
    _cache.clear()
