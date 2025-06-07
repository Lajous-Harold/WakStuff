import os

FOLDER = "data"

def delete_json_files(folder):
    if not os.path.exists(folder):
        print(f"[FAIL] Le dossier '{folder}' n'existe pas.")
        return

    deleted = 0
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            filepath = os.path.join(folder, filename)
            try:
                os.remove(filepath)
                print(f"[OK] Supprimé : {filename}")
                deleted += 1
            except Exception as e:
                print(f"[FAIL] Erreur suppression {filename} : {e}")

    if deleted == 0:
        print("[INFO] Aucun fichier .json trouvé.")
    else:
        print(f"[INFO] {deleted} fichiers .json supprimés.")

if __name__ == "__main__":
    delete_json_files(FOLDER)
