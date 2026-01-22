"""
Nunchi Dashboard Configuration
Contract addresses and event signatures for HyperEVM
"""

# HyperEVM RPC
RPC_URL = "https://hyperliquid.drpc.org"
CHAIN_ID = 999

# Contract Addresses
CONTRACTS = {
    "wNLP": "0x4Cc221cf1444333510a634CE0D8209D2D11B9bbA",
    "SY_wNLP": "0x9b7430dB2C59247E861702B5C85131eEaf03aED3",
    "PENDLE_ROUTER": "0x888888888889758f76e7103c6cbf23abbf58f946",
    "nHYPE": "0x88888884cdc539d00dfb9C9e2Af81baA65fDA356",
}

# Pendle Markets (multiple pools for wNLP)
PENDLE_MARKETS = {
    "26 Dec 2025": {
        "market": "0x07a50aEc9B49cD605e66B0cA7e39d781E6Ae0b79",
        "pt": "0x17a885bb988353f430141890b41f787debc3e107",
        "yt": "0x1f6EA7A91477523b9EAD6DB13f1373eAEB312952",
        "expiry": "2025-12-26",
    },
    "25 Jun 2026": {
        "market": "0xc1ef65d86f82d5a8160b577a150f65d52d6b266f",
        "pt": "0x4eb660811bcb71174b04a1f102f784efe794a66b",
        "yt": None,
        "expiry": "2026-06-25",
    },
}

# Event Topic Signatures (keccak256 hashes)
EVENTS = {
    # ERC-20 Transfer(address indexed from, address indexed to, uint256 value)
    "TRANSFER": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",

    # Pendle Swap(address indexed caller, address indexed receiver, int256 netPtOut, int256 netSyOut, uint256 netSyFee, uint256 netSyToReserve)
    "SWAP": "0x829000a5bc6a12d46e30cdcecd7c56b1efd88f6d7d059da6734a04f3764557c4",

    # Pendle Mint(address indexed receiver, uint256 netLpMinted, uint256 netSyUsed, uint256 netPtUsed)
    "MINT": "0xb4c03061fb5b7fed76389d5af8f2e0ddb09f8c70d1333abbb62582835e10accb",

    # Pendle Burn(address indexed receiverSy, address indexed receiverPt, uint256 netLpBurned, uint256 netSyOut, uint256 netPtOut)
    "BURN": "0x4cf25bc1d991c17529c25213d3cc0cdb935e6805f54b7b3c66c68b92c6f39d00",

    # RedeemRewards(address indexed user, uint256[] rewardsOut)
    "REDEEM_REWARDS": "0x78d61a0c27b13f43911095f9f356f14daa3cd8b125eea1aa22421245e90e813d",
}

# Zero address for detecting mints/burns
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"

# Token decimals (wNLP and SY tokens use 6 decimals)
TOKEN_DECIMALS = 6

# Dashboard settings
CACHE_TTL = 300  # 5 minutes
DEFAULT_DAYS = 1  # Start with 1 day for fastest load
