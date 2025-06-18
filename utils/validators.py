
import re
from datetime import datetime
from typing import Optional


def validate_chess_id(chess_id: str) -> bool:
    """
    Valide un identifiant national d'échecs
    
    Args:
        chess_id (str): Identifiant à valider (format: AB12345)
        
    Returns:
        bool: True si valide, False sinon
    """
    if not chess_id or not isinstance(chess_id, str):
        return False
        
    chess_id = chess_id.strip().upper()
    
    # Pattern : 2 lettres + 5 chiffres
    pattern = r'^[A-Z]{2}\d{5}$'
    return bool(re.match(pattern, chess_id))


def validate_name(name: str) -> bool:
    """
    Valide un nom ou prénom
    
    Args:
        name (str): Nom à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not name or not isinstance(name, str):
        return False
        
    name = name.strip()
    
    # Minimum 2 caractères, lettres, espaces, tirets, apostrophes
    if len(name) < 2:
        return False
        
    # Pattern : lettres, espaces, tirets, apostrophes, accents
    pattern = r"^[a-zA-ZÀ-ÿ\s\-']+$"
    return bool(re.match(pattern, name))


def validate_date_format(date_str: str) -> bool:
    """
    Valide le format d'une date
    
    Args:
        date_str (str): Date à valider (format: YYYY-MM-DD)
        
    Returns:
        bool: True si valide, False sinon
    """
    if not date_str or not isinstance(date_str, str):
        return False
        
    try:
        datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_score(score: float) -> bool:
    """
    Valide un score d'échecs
    
    Args:
        score (float): Score à valider (0, 0.5 ou 1)
        
    Returns:
        bool: True si valide, False sinon
    """
    if not isinstance(score, (int, float)):
        return False
        
    return score in [0, 0.5, 1, 0.0, 1.0]


def validate_email(email: str) -> bool:
    """
    Valide un format d'email (optionnel pour les joueurs)
    
    Args:
        email (str): Email à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not email or not isinstance(email, str):
        return False
        
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Valide un numéro de téléphone français (optionnel)
    
    Args:
        phone (str): Numéro à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not phone or not isinstance(phone, str):
        return False
        
    # Supprimer espaces et tirets
    phone = re.sub(r'[\s\-\.]', '', phone)
    
    # Pattern français : 10 chiffres commençant par 0
    pattern = r'^0[1-9]\d{8}$'
    return bool(re.match(pattern, phone))


def validate_tournament_name(name: str) -> bool:
    """
    Valide le nom d'un tournoi
    
    Args:
        name (str): Nom du tournoi
        
    Returns:
        bool: True si valide, False sinon
    """
    if not name or not isinstance(name, str):
        return False
        
    name = name.strip()
    
    # Minimum 3 caractères, maximum 100
    if len(name) < 3 or len(name) > 100:
        return False
        
    # Lettres, chiffres, espaces, tirets, apostrophes
    pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-'\.]+$"
    return bool(re.match(pattern, name))


def validate_location(location: str) -> bool:
    """
    Valide un lieu de tournoi
    
    Args:
        location (str): Lieu à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not location or not isinstance(location, str):
        return False
        
    location = location.strip()
    
    # Minimum 2 caractères, maximum 200
    if len(location) < 2 or len(location) > 200:
        return False
        
    # Lettres, chiffres, espaces, tirets, apostrophes, virgules
    pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-',\.]+$"
    return bool(re.match(pattern, location))


def validate_positive_integer(value: int, min_val: int = 1, max_val: int = 100) -> bool:
    """
    Valide un entier positif dans une plage
    
    Args:
        value (int): Valeur à valider
        min_val (int): Valeur minimale
        max_val (int): Valeur maximale
        
    Returns:
        bool: True si valide, False sinon
    """
    if not isinstance(value, int):
        return False
        
    return min_val <= value <= max_val


def sanitize_string(text: str) -> str:
    """
    Nettoie une chaîne de caractères
    
    Args:
        text (str): Texte à nettoyer
        
    Returns:
        str: Texte nettoyé
    """
    if not text or not isinstance(text, str):
        return ""
        
    # Supprimer espaces début/fin et normaliser
    text = text.strip()
    
    # Supprimer caractères de contrôle
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    # Normaliser espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    return text


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Valide que la date de fin est après la date de début
    
    Args:
        start_date (str): Date de début (YYYY-MM-DD)
        end_date (str): Date de fin (YYYY-MM-DD)
        
    Returns:
        bool: True si valide, False sinon
    """
    if not validate_date_format(start_date) or not validate_date_format(end_date):
        return False
        
    try:
        start = datetime.strptime(start_date.strip(), '%Y-%m-%d')
        end = datetime.strptime(end_date.strip(), '%Y-%m-%d')
        return end >= start
    except ValueError:
        return False


def validate_age_range(birthdate: str, min_age: int = 0, max_age: int = 120) -> bool:
    """
    Valide qu'un âge est dans une plage acceptable
    
    Args:
        birthdate (str): Date de naissance (YYYY-MM-DD)
        min_age (int): Âge minimal
        max_age (int): Âge maximal
        
    Returns:
        bool: True si valide, False sinon
    """
    if not validate_date_format(birthdate):
        return False
        
    try:
        birth = datetime.strptime(birthdate.strip(), '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return min_age <= age <= max_age
    except ValueError:
        return False


def get_validation_errors(data: dict, field_validators: dict) -> list:
    """
    Valide un dictionnaire de données selon des règles définies
    
    Args:
        data (dict): Données à valider
        field_validators (dict): Validateurs par champ
        
    Returns:
        list: Liste des erreurs trouvées
    """
    errors = []
    
    for field, validator in field_validators.items():
        if field not in data:
            errors.append(f"Champ manquant: {field}")
            continue
            
        value = data[field]
        
        if callable(validator):
            if not validator(value):
                errors.append(f"Valeur invalide pour {field}: {value}")
        elif isinstance(validator, dict):
            # Validateur avec paramètres
            func = validator.get('func')
            if func and callable(func):
                kwargs = {k: v for k, v in validator.items() if k != 'func'}
                if not func(value, **kwargs):
                    errors.append(f"Valeur invalide pour {field}: {value}")
                    
    return errors