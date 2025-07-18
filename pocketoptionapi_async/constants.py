"""
Constants and configuration for the PocketOption API
"""

from typing import Dict, List
import random

# Asset mappings with their corresponding IDs

ASSETS: Dict[str, int] = {
    
    "#AAPL": 5,
    "#AAPL_otc": 170,
    "#AXP": 140,
    "#AXP_otc": 291,
    "#BA": 8,
    "#BA_otc": 292,
    "#CSCO": 154,
    "#CSCO_otc": 427,
    "#FB": 177,
    "#FB_otc": 187,
    "#INTC": 180,
    "#INTC_otc": 190,
    "#JNJ": 144,
    "#JNJ_otc": 296,
    "#JPM": 20,
    "#MCD": 23,
    "#MCD_otc": 175,
    "#MSFT": 24,
    "#MSFT_otc": 176,
    "#PFE": 147,
    "#PFE_otc": 297,
    "#TSLA": 186,
    "#TSLA_otc": 196,
    "#XOM": 153,
    "#XOM_otc": 426,
    "100GBP": 315,
    "100GBP_otc": 403,
    "ADA-USD_otc": 473,
    "AEDCNY_otc": 538,
    "AEX25": 449,
    "AMD_otc": 568,
    "AMZN_otc": 412,
    "AUDCAD": 36,
    "AUDCAD_otc": 67,
    "AUDCHF": 37,
    "AUDCHF_otc": 68,
    "AUDJPY": 38,
    "AUDJPY_otc": 69,
    "AUDNZD_otc": 70,
    "AUDUSD": 40,
    "AUDUSD_otc": 71,
    "AUS200": 305,
    "AUS200_otc": 306,
    "AVAX_otc": 481,
    "BABA": 183,
    "BABA_otc": 428,
    "BCHEUR": 450,
    "BCHGBP": 451,
    "BCHJPY": 452,
    "BHDCNY_otc": 536,
    "BITB_otc": 494,
    "BNB-USD_otc": 470,
    "BTCGBP": 453,
    "BTCJPY": 454,
    "BTCUSD": 197,
    "BTCUSD_otc": 484,
    "CAC40": 455,
    "CADCHF": 41,
    "CADCHF_otc": 72,
    "CADJPY": 42,
    "CADJPY_otc": 73,
    "CHFJPY": 43,
    "CHFJPY_otc": 74,
    "CHFNOK_otc": 457,
    "CITI": 326,
    "CITI_otc": 413,
    "COIN_otc": 570,
    "D30EUR": 318,
    "D30EUR_otc": 406,
    "DASH_USD": 209,
    "DJI30": 322,
    "DJI30_otc": 409,
    "DOGE_otc": 485,
    "DOTUSD_otc": 486,
    "E35EUR": 314,
    "E35EUR_otc": 402,
    "E50EUR": 319,
    "E50EUR_otc": 407,
    "ETHUSD": 272,
    "ETHUSD_otc": 487,
    "EURAUD": 44,
    "EURCAD": 45,
    "EURCHF": 46,
    "EURCHF_otc": 77,
    "EURGBP": 47,
    "EURGBP_otc": 78,
    "EURHUF_otc": 460,
    "EURJPY": 48,
    "EURJPY_otc": 79,
    "EURNZD_otc": 80,
    "EURRUB_otc": 200,
    "EURTRY_otc": 468,
    "EURUSD": 1,
    "EURUSD_otc": 66,
    "F40EUR": 316,
    "F40EUR_otc": 404,
    "FDX_otc": 414,
    "GBPAUD": 51,
    "GBPAUD_otc": 81,
    "GBPCAD": 52,
    "GBPCHF": 53,
    "GBPJPY": 54,
    "GBPJPY_otc": 84,
    "GBPUSD": 56,
    "GBPUSD_otc": 86,
    "GME_otc": 566,
    "H33HKD": 463,
    "IRRUSD_otc": 548,
    "JODCNY_otc": 546,
    "JPN225": 317,
    "JPN225_otc": 405,
    "KESUSD_otc": 554,
    "LBPUSD_otc": 530,
    "LINK_otc": 478,
    "LNKUSD": 464,
    "LTCUSD_otc": 488,
    "MADUSD_otc": 534,
    "MARA_otc": 572,
    "MATIC_otc": 491,
    "NASUSD": 323,
    "NASUSD_otc": 410,
    "NFLX": 182,
    "NFLX_otc": 429,
    "NGNUSD_otc": 552,
    "NZDJPY_otc": 89,
    "NZDUSD_otc": 90,
    "OMRCNY_otc": 544,
    "PLTR_otc": 562,
    "QARCNY_otc": 542,
    "SARCNY_otc": 540,
    "SMI20": 466,
    "SOL-USD_otc": 472,
    "SP500": 321,
    "SP500_otc": 408,
    "SYPUSD_otc": 550,
    "TNDUSD_otc": 532,
    "TON-USD_otc": 480,
    "TRX-USD_otc": 476,
    "UAHUSD_otc": 558,
    "UKBrent": 50,
    "UKBrent_otc": 164,
    "USCrude": 64,
    "USCrude_otc": 165,
    "USDARS_otc": 506,
    "USDBDT_otc": 500,
    "USDBRL_otc": 502,
    "USDCAD": 61,
    "USDCAD_otc": 91,
    "USDCHF": 62,
    "USDCHF_otc": 92,
    "USDCLP_otc": 525,
    "USDCNH_otc": 467,
    "USDCOP_otc": 515,
    "USDDZD_otc": 508,
    "USDEGP_otc": 513,
    "USDIDR_otc": 504,
    "USDINR_otc": 202,
    "USDJPY": 63,
    "USDJPY_otc": 93,
    "USDMXN_otc": 509,
    "USDMYR_otc": 523,
    "USDPHP_otc": 511,
    "USDPKR_otc": 517,
    "USDRUB_otc": 199,
    "USDSGD_otc": 526,
    "USDTHB_otc": 521,
    "USDVND_otc": 519,
    "VISA_otc": 416,
    "VIX_otc": 560,
    "XAGEUR": 103,
    "XAGUSD": 65,
    "XAGUSD_otc": 167,
    "XAUEUR": 102,
    "XAUUSD": 2,
    "XAUUSD_otc": 169,
    "XNGUSD": 311,
    "XNGUSD_otc": 399,
    "XPDUSD": 313,
    "XPDUSD_otc": 401,
    "XPTUSD": 312,
    "XPTUSD_otc": 400,
    "YERUSD_otc": 528,
    "ZARUSD_otc": 556
}

# WebSocket regions with their URLs
class Regions:
    """WebSocket region endpoints"""

    _REGIONS = {
        "EUROPA": "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket",
        "SEYCHELLES": "wss://api-sc.po.market/socket.io/?EIO=4&transport=websocket",
        "HONGKONG": "wss://api-hk.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER1": "wss://api-spb.po.market/socket.io/?EIO=4&transport=websocket",
        "FRANCE2": "wss://api-fr2.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES4": "wss://api-us4.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES3": "wss://api-us3.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES2": "wss://api-us2.po.market/socket.io/?EIO=4&transport=websocket",
        "DEMO": "wss://demo-api-eu.po.market/socket.io/?EIO=4&transport=websocket",
        "DEMO_2": "wss://try-demo-eu.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES": "wss://api-us-north.po.market/socket.io/?EIO=4&transport=websocket",
        "RUSSIA": "wss://api-msk.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER2": "wss://api-l.po.market/socket.io/?EIO=4&transport=websocket",
        "INDIA": "wss://api-in.po.market/socket.io/?EIO=4&transport=websocket",
        "FRANCE": "wss://api-fr.po.market/socket.io/?EIO=4&transport=websocket",
        "FINLAND": "wss://api-fin.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER3": "wss://api-c.po.market/socket.io/?EIO=4&transport=websocket",
        "ASIA": "wss://api-asia.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER4": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket",
    }

    @classmethod
    def get_all(cls, randomize: bool = True) -> List[str]:
        """Get all region URLs"""
        urls = list(cls._REGIONS.values())
        if randomize:
            random.shuffle(urls)
        return urls

    @classmethod
    def get_all_regions(cls) -> Dict[str, str]:
        """Get all regions as a dictionary"""
        return cls._REGIONS.copy()

    from typing import Optional

    @classmethod
    def get_region(cls, region_name: str) -> Optional[str]:
        """Get specific region URL"""
        return cls._REGIONS.get(region_name.upper())

    @classmethod
    def get_demo_regions(cls) -> List[str]:
        """Get demo region URLs"""
        return [url for name, url in cls._REGIONS.items() if "DEMO" in name]


# Global constants
REGIONS = Regions()

# Timeframes (in seconds)
TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "1w": 604800,
}

# Connection settings
CONNECTION_SETTINGS = {
    "ping_interval": 20,  # seconds
    "ping_timeout": 10,  # seconds
    "close_timeout": 10,  # seconds
    "max_reconnect_attempts": 5,
    "reconnect_delay": 5,  # seconds
    "message_timeout": 30,  # seconds
}

# API Limits
API_LIMITS = {
    "min_order_amount": 1.0,
    "max_order_amount": 50000.0,
    "min_duration": 5,  # seconds
    "max_duration": 43200,  # 12 hours in seconds
    "max_concurrent_orders": 10,
    "rate_limit": 100,  # requests per minute
}

# Default headers
DEFAULT_HEADERS = {
    "Origin": "https://pocketoption.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
