import os
import requests
import time
from config import BASE_URL, CONFIG_URL, TYPES, RAW_DIR, HEADERS, LOG_FILE
from utils import log, save_json

def fetch_version():
    log("[INFO] Récupération version depuis config.json")
    r = requests.get(CONFIG_URL, headers=HEADERS)
    if r.ok:
        version = r.json().get("version")
        log(f"[OK] Version détectée : {version}")
        return version
    else:
        log(f"[FAIL] Erreur accès version (code {r.status_code})")
        return None

def download_json_files(version):
    os.makedirs(RAW_DIR, exist_ok=True)
    for type_ in TYPES:
        url = f"{BASE_URL}/{version}/{type_}.json"
        path = os.path.join(RAW_DIR, f"{type_}.json")
        log(f"[INFO] Téléchargement de {type_}.json...")
        start = time.time()
        try:
            r = requests.get(url, headers=HEADERS)
            r.raise_for_status()
            save_json(r.json(), path)
            log(f"[OK] {type_}.json téléchargé ({time.time() - start:.2f} sec)")
        except Exception as e:
            log(f"[FAIL] {type_}.json : {e}")

if __name__ == "__main__":
    # Reset log si appelé en direct
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")
    log("[INFO] Lancement manuel de fetcher.py")
    start = time.time()

    version = fetch_version()
    if version:
        download_json_files(version)

    log(f"[INFO] fetcher.py terminé en {time.time() - start:.2f} secondes.")
