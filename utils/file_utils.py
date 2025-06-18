
import os
import json
import shutil
import tempfile
from typing import Any, Optional, Dict
from pathlib import Path


def ensure_directory_exists(directory_path: str) -> bool:
    """
    S'assure qu'un répertoire existe, le crée si nécessaire
    
    Args:
        directory_path (str): Chemin du répertoire
        
    Returns:
        bool: True si le répertoire existe ou a été créé
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Erreur création répertoire {directory_path}: {e}")
        return False


def safe_json_save(data: Any, file_path: str) -> bool:
    """
    Sauvegarde sécurisée d'un fichier JSON avec fichier temporaire
    
    Args:
        data (Any): Données à sauvegarder
        file_path (str): Chemin du fichier de destination
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Créer le répertoire parent si nécessaire
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not ensure_directory_exists(parent_dir):
            return False
        
        # Écriture dans un fichier temporaire d'abord
        temp_file = f"{file_path}.tmp"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Déplacer le fichier temporaire vers la destination
        shutil.move(temp_file, file_path)
        return True
        
    except Exception as e:
        print(f"Erreur sauvegarde JSON {file_path}: {e}")
        # Nettoyer le fichier temporaire en cas d'erreur
        try:
            if os.path.exists(f"{file_path}.tmp"):
                os.remove(f"{file_path}.tmp")
        except Exception:
            pass
        return False


def safe_json_load(file_path: str) -> Optional[Any]:
    """
    Chargement sécurisé d'un fichier JSON
    
    Args:
        file_path (str): Chemin du fichier à charger
        
    Returns:
        Optional[Any]: Données chargées ou None si erreur
    """
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


def backup_file(file_path: str, backup_dir: str = None) -> Optional[str]:
    """
    Crée une sauvegarde d'un fichier
    
    Args:
        file_path (str): Fichier à sauvegarder
        backup_dir (str): Répertoire de sauvegarde (optionnel)
        
    Returns:
        Optional[str]: Chemin du fichier de sauvegarde ou None
    """
    try:
        if not os.path.exists(file_path):
            return None
            
        # Déterminer le répertoire de backup
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), 'backups')
        
        ensure_directory_exists(backup_dir)
        
        # Nom du fichier de backup avec timestamp
        import time
        timestamp = int(time.time())
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.{timestamp}.backup"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copier le fichier
        shutil.copy2(file_path, backup_path)
        return backup_path
        
    except Exception as e:
        print(f"Erreur backup {file_path}: {e}")
        return None


def restore_from_backup(backup_path: str, destination_path: str) -> bool:
    """
    Restaure un fichier depuis une sauvegarde
    
    Args:
        backup_path (str): Chemin de la sauvegarde
        destination_path (str): Chemin de destination
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        if not os.path.exists(backup_path):
            return False
            
        # Créer le répertoire de destination si nécessaire
        parent_dir = os.path.dirname(destination_path)
        if parent_dir and not ensure_directory_exists(parent_dir):
            return False
            
        shutil.copy2(backup_path, destination_path)
        return True
        
    except Exception as e:
        print(f"Erreur restauration {backup_path}: {e}")
        return False


def get_file_size(file_path: str) -> int:
    """
    Retourne la taille d'un fichier en octets
    
    Args:
        file_path (str): Chemin du fichier
        
    Returns:
        int: Taille en octets ou 0 si erreur
    """
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


def get_file_modification_time(file_path: str) -> float:
    """
    Retourne le timestamp de dernière modification
    
    Args:
        file_path (str): Chemin du fichier
        
    Returns:
        float: Timestamp ou 0 si erreur
    """
    try:
        return os.path.getmtime(file_path)
    except Exception:
        return 0.0


def cleanup_temp_files(directory: str, pattern: str = "*.tmp") -> int:
    """
    Nettoie les fichiers temporaires dans un répertoire
    
    Args:
        directory (str): Répertoire à nettoyer
        pattern (str): Pattern des fichiers à supprimer
        
    Returns:
        int: Nombre de fichiers supprimés
    """
    try:
        if not os.path.exists(directory):
            return 0
            
        import glob
        temp_files = glob.glob(os.path.join(directory, pattern))
        count = 0
        
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                count += 1
            except Exception:
                continue
                
        return count
        
    except Exception:
        return 0


def validate_json_structure(file_path: str, required_keys: list) -> bool:
    """
    Valide la structure d'un fichier JSON
    
    Args:
        file_path (str): Chemin du fichier JSON
        required_keys (list): Clés requises
        
    Returns:
        bool: True si structure valide, False sinon
    """
    try:
        data = safe_json_load(file_path)
        if data is None:
            return False
            
        if isinstance(data, dict):
            return all(key in data for key in required_keys)
        elif isinstance(data, list) and data:
            # Vérifier le premier élément de la liste
            return all(key in data[0] for key in required_keys)
        else:
            return False
            
    except Exception:
        return False


def compress_file(file_path: str, compressed_path: str = None) -> Optional[str]:
    """
    Compresse un fichier avec gzip
    
    Args:
        file_path (str): Fichier à compresser
        compressed_path (str): Chemin du fichier compressé (optionnel)
        
    Returns:
        Optional[str]: Chemin du fichier compressé ou None
    """
    try:
        import gzip
        
        if not os.path.exists(file_path):
            return None
            
        if compressed_path is None:
            compressed_path = f"{file_path}.gz"
            
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        return compressed_path
        
    except Exception as e:
        print(f"Erreur compression {file_path}: {e}")
        return None


def decompress_file(compressed_path: str, output_path: str = None) -> Optional[str]:
    """
    Décompresse un fichier gzip
    
    Args:
        compressed_path (str): Fichier compressé
        output_path (str): Chemin de sortie (optionnel)
        
    Returns:
        Optional[str]: Chemin du fichier décompressé ou None
    """
    try:
        import gzip
        
        if not os.path.exists(compressed_path):
            return None
            
        if output_path is None:
            if compressed_path.endswith('.gz'):
                output_path = compressed_path[:-3]
            else:
                output_path = f"{compressed_path}.decompressed"
                
        with gzip.open(compressed_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        return output_path
        
    except Exception as e:
        print(f"Erreur décompression {compressed_path}: {e}")
        return None


def copy_file_safely(source: str, destination: str, backup_existing: bool = True) -> bool:
    """
    Copie un fichier de manière sécurisée
    
    Args:
        source (str): Fichier source
        destination (str): Fichier destination
        backup_existing (bool): Sauvegarder le fichier existant
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        if not os.path.exists(source):
            return False
            
        # Créer le répertoire de destination
        parent_dir = os.path.dirname(destination)
        if parent_dir and not ensure_directory_exists(parent_dir):
            return False
            
        # Sauvegarder le fichier existant si demandé
        if backup_existing and os.path.exists(destination):
            backup_file(destination)
            
        # Copier avec un fichier temporaire
        temp_dest = f"{destination}.copying"
        shutil.copy2(source, temp_dest)
        shutil.move(temp_dest, destination)
        
        return True
        
    except Exception as e:
        print(f"Erreur copie {source} vers {destination}: {e}")
        # Nettoyer le fichier temporaire
        try:
            if os.path.exists(f"{destination}.copying"):
                os.remove(f"{destination}.copying")
        except Exception:
            pass
        return False


def get_directory_size(directory: str) -> int:
    """
    Calcule la taille totale d'un répertoire
    
    Args:
        directory (str): Chemin du répertoire
        
    Returns:
        int: Taille totale en octets
    """
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except Exception:
                    continue
        return total_size
    except Exception:
        return 0


def cleanup_old_backups(backup_dir: str, max_backups: int = 10) -> int:
    """
    Nettoie les anciens fichiers de sauvegarde
    
    Args:
        backup_dir (str): Répertoire des sauvegardes
        max_backups (int): Nombre maximum de sauvegardes à conserver
        
    Returns:
        int: Nombre de fichiers supprimés
    """
    try:
        if not os.path.exists(backup_dir):
            return 0
            
        # Lister tous les fichiers de backup
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.backup'):
                file_path = os.path.join(backup_dir, filename)
                mtime = os.path.getmtime(file_path)
                backup_files.append((mtime, file_path))
                
        # Trier par date de modification (plus récent en premier)
        backup_files.sort(reverse=True)
        
        # Supprimer les anciens fichiers
        deleted_count = 0
        for i, (_, file_path) in enumerate(backup_files):
            if i >= max_backups:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception:
                    continue
                    
        return deleted_count
        
    except Exception:
        return 0