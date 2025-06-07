import os
import json

SOURCE_DIR = "data"
PREVIEW_DIR = "preview"
FILES = [
    "items.json",
    "equipmentItemTypes.json",
    "itemTypes.json",
    "itemProperties.json",
    "actions.json",
    "states.json"
]

def load_json_file(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_preview(name, content):
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    preview_path = os.path.join(PREVIEW_DIR, name)
    with open(preview_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4, ensure_ascii=False)
    print(f"[OK] Échantillon enregistré : {preview_path}")

def main():
    for file in FILES:
        src_path = os.path.join(SOURCE_DIR, file)
        if not os.path.exists(src_path):
            print(f"[WARN] Fichier non trouvé : {src_path}")
            continue
        try:
            data = load_json_file(src_path)
            sample = data[:5] if isinstance(data, list) else dict(list(data.items())[:5])
            save_preview(file, sample)
        except Exception as e:
            print(f"[FAIL] Erreur traitement {file} : {e}")

if __name__ == "__main__":
    main()
