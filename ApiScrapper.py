import os
import time
import requests
from datetime import datetime

# ========== CONFIGURATION ==========
config_url = "https://wakfu.cdn.ankama.com/gamedata/config.json"
essential_files = [
    "items.json",
    "actions.json",
    "equipmentItemTypes.json",
    "itemProperties.json",
    "states.json",
    "itemTypes.json",
    "recipes.json",
    "recipeIngredients.json",
    "recipeResults.json",
    "jobsItems.json"
]
output_dir = "./wakfu_api_json"
log_file = "log.txt"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ========== LOGGING UTILS ==========
log_lines = []

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    log_lines.append(line)

def save_log():
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

# ========== START SCRIPT ==========
script_start = time.time()
log("[INFO] Démarrage du script de récupération JSON Wakfu")

# 1. Récupérer la version actuelle
try:
    log(f"[INFO] Tentative de récupération de la version depuis {config_url}")
    r = requests.get(config_url, headers=headers)
    r.raise_for_status()
    version = r.json().get("currentVersion", "1.87.2")
    log(f"[OK] Version détectée : {version}")
except Exception as e:
    version = "1.87.2"
    log(f"[FAIL] Impossible de récupérer la version, utilisation par défaut : {version} ({e})")

# 2. Créer le dossier
os.makedirs(output_dir, exist_ok=True)

# 3. Télécharger les fichiers
for filename in essential_files:
    url = f"https://wakfu.cdn.ankama.com/gamedata/{version}/{filename}"
    path = os.path.join(output_dir, filename)
    start = time.time()
    try:
        log(f"[INFO] Téléchargement de {filename}...")
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        with open(path, "w", encoding="utf-8") as f:
            f.write(r.text)
        duration = round(time.time() - start, 2)
        log(f"[OK] {filename} téléchargé ({duration} sec)")
    except Exception as e:
        log(f"[FAIL] {filename} — erreur : {e}")

# 4. Fin du script
total_duration = round(time.time() - script_start, 2)
log(f"[INFO] Script terminé en {total_duration} secondes")

# 5. Sauvegarde du log
save_log()
log(f"[INFO] Log écrit dans {log_file}")
