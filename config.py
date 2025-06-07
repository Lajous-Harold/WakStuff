BASE_URL = "https://wakfu.cdn.ankama.com/gamedata"
CONFIG_URL = f"{BASE_URL}/config.json"
HEADERS = {"User-Agent": "WakStuffDataFetcher/1.0"}

TYPES = [
    "items", "actions", "equipmentItemTypes",
    "itemTypes", "itemProperties", "states"
]

RAW_DIR = "data"
OUT_DIR = "output"
LOG_FILE = "log.txt"
