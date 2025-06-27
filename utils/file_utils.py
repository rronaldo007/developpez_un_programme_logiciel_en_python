import os
import json
import shutil
from typing import Any, Optional
from pathlib import Path


def ensure_directory_exists(directory_path: str) -> bool:
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Erreur création répertoire {directory_path}: {e}")
        return False


def safe_json_save(data: Any, file_path: str) -> bool:
    try:
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not ensure_directory_exists(parent_dir):
            return False

        temp_file = f"{file_path}.tmp"

        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        shutil.move(temp_file, file_path)
        return True

    except Exception as e:
        print(f"Erreur sauvegarde JSON {file_path}: {e}")
        try:
            if os.path.exists(f"{file_path}.tmp"):
                os.remove(f"{file_path}.tmp")
        except Exception:
            pass
        return False


def safe_json_load(file_path: str) -> Optional[Any]:
    try:
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        print(f"Erreur format JSON {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Erreur chargement {file_path}: {e}")
        return None
