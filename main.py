import time
from fetcher import fetch_version, download_json_files
from processor import enrich_items
from utils import log
from config import LOG_FILE

def main():
    with open(LOG_FILE, "w", encoding="utf-8") as f: f.write("")
    start = time.time()
    log("[INFO] Démarrage du script WakStuff")

    version = fetch_version()
    if not version:
        return
    download_json_files(version)
    enrich_items()

    log(f"[INFO] Script terminé en {time.time() - start:.2f} secondes.")

if __name__ == "__main__":
    main()
