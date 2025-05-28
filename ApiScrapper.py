import os
import requests
import json
import time
from datetime import datetime

# ========== CONFIGURATION ==========
BASE_URL = "https://wakfu.cdn.ankama.com/gamedata"
CONFIG_URL = f"{BASE_URL}/config.json"
OUTPUT_DIR = "wakfu_api_json"
HEADERS = {
    "User-Agent": "WakStuffDataFetcher/1.0"
}
TYPES = [
    "items",                  # Objets + effets
    "actions",                # Définition des effets
    "equipmentItemTypes",     # Types d’équipements (ex: casque, anneau...)
    "itemProperties",         # Propriétés spéciales (ex: épique, relique…)
    "itemTypes",              # Catégorisation des items
    "states"                  # États appliqués via objets ou effets
]
LOG_FILE = "log.txt"

# ========== FONCTIONS ==========

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def fetch_version():
    r = requests.get(CONFIG_URL, headers=HEADERS)
    if r.status_code == 200:
        try:
            version = r.json()["version"]
            log(f"[OK] Version détectée : {version}")
            return version
        except Exception as e:
            log(f"[FAIL] Erreur de parsing JSON version : {e}")
    else:
        log(f"[FAIL] Impossible d'accéder à config.json (code {r.status_code})")
    return None

def download_and_format_json(version, type_):
    url = f"{BASE_URL}/{version}/{type_}.json"
    filepath = os.path.join(OUTPUT_DIR, f"{type_}.json")

    try:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        data = r.json()  # Vérifie que le JSON est valide
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log(f"[OK] Téléchargé et formaté : {type_}.json")
    except Exception as e:
        log(f"[FAIL] Échec pour {type_}.json : {e}")

# ========== SCRIPT PRINCIPAL ==========

def main():
    start_time = time.time()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        log(f"[OK] Dossier créé : {OUTPUT_DIR}")

    version = fetch_version()
    if not version:
        return

    for type_ in TYPES:
        download_and_format_json(version, type_)

    elapsed = time.time() - start_time
    log(f"[INFO] Téléchargement terminé en {elapsed:.2f} secondes.")

if __name__ == "__main__":
    main()
