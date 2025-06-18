
from datetime import datetime, timedelta
from typing import Optional
import time


def get_current_timestamp() -> str:
    """
    Retourne le timestamp actuel au format ISO
    
    Returns:
        str: Timestamp ISO format
    """
    return datetime.now().isoformat()


def get_current_date() -> str:
    """
    Retourne la date actuelle au format YYYY-MM-DD
    
    Returns:
        str: Date au format YYYY-MM-DD
    """
    return datetime.now().strftime('%Y-%m-%d')


def calculate_age(birthdate: str, reference_date: Optional[str] = None) -> Optional[int]:
    """
    Calcule l'âge d'une personne
    
    Args:
        birthdate (str): Date de naissance (YYYY-MM-DD)
        reference_date (Optional[str]): Date de référence (défaut: aujourd'hui)
        
    Returns:
        Optional[int]: Âge en années ou None si erreur
    """
    try:
        birth = datetime.strptime(birthdate, '%Y-%m-%d')
        
        if reference_date:
            ref = datetime.strptime(reference_date, '%Y-%m-%d')
        else:
            ref = datetime.now()
            
        age = ref.year - birth.year
        
        # Ajuster si l'anniversaire n'est pas encore passé cette année
        if (ref.month, ref.day) < (birth.month, birth.day):
            age -= 1
            
        return age if age >= 0 else None
        
    except ValueError:
        return None


def calculate_duration_minutes(start_timestamp: str, end_timestamp: str) -> Optional[int]:
    """
    Calcule la durée entre deux timestamps en minutes
    
    Args:
        start_timestamp (str): Timestamp de début
        end_timestamp (str): Timestamp de fin
        
    Returns:
        Optional[int]: Durée en minutes ou None si erreur
    """
    try:
        start = datetime.fromisoformat(start_timestamp)
        end = datetime.fromisoformat(end_timestamp)
        
        duration = end - start
        return int(duration.total_seconds() / 60)
        
    except (ValueError, TypeError):
        return None


def format_timestamp_display(timestamp: str, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formate un timestamp pour l'affichage
    
    Args:
        timestamp (str): Timestamp ISO
        format_str (str): Format de sortie
        
    Returns:
        str: Timestamp formaté
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime(format_str)
    except (ValueError, TypeError):
        return timestamp


def is_date_in_past(date_str: str) -> bool:
    """
    Vérifie si une date est dans le passé
    
    Args:
        date_str (str): Date à vérifier (YYYY-MM-DD)
        
    Returns:
        bool: True si la date est passée
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.date() < datetime.now().date()
    except ValueError:
        return False


def is_date_in_future(date_str: str) -> bool:
    """
    Vérifie si une date est dans le futur
    
    Args:
        date_str (str): Date à vérifier (YYYY-MM-DD)
        
    Returns:
        bool: True si la date est future
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.date() > datetime.now().date()
    except ValueError:
        return False


def add_days_to_date(date_str: str, days: int) -> str:
    """
    Ajoute des jours à une date
    
    Args:
        date_str (str): Date de base (YYYY-MM-DD)
        days (int): Nombre de jours à ajouter
        
    Returns:
        str: Nouvelle date (YYYY-MM-DD)
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        new_date = date_obj + timedelta(days=days)
        return new_date.strftime('%Y-%m-%d')
    except ValueError:
        return date_str


def get_date_range_days(start_date: str, end_date: str) -> Optional[int]:
    """
    Calcule le nombre de jours entre deux dates
    
    Args:
        start_date (str): Date de début (YYYY-MM-DD)
        end_date (str): Date de fin (YYYY-MM-DD)
        
    Returns:
        Optional[int]: Nombre de jours ou None si erreur
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        duration = end - start
        return duration.days
        
    except ValueError:
        return None


def get_week_number(date_str: str) -> Optional[int]:
    """
    Retourne le numéro de semaine d'une date
    
    Args:
        date_str (str): Date (YYYY-MM-DD)
        
    Returns:
        Optional[int]: Numéro de semaine ou None si erreur
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.isocalendar()[1]
    except ValueError:
        return None


def get_month_name(date_str: str, lang: str = "fr") -> str:
    """
    Retourne le nom du mois d'une date
    
    Args:
        date_str (str): Date (YYYY-MM-DD)
        lang (str): Langue ("fr" ou "en")
        
    Returns:
        str: Nom du mois
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month_num = date_obj.month
        
        if lang == "fr":
            months_fr = [
                "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
            ]
            return months_fr[month_num - 1]
        else:
            return date_obj.strftime('%B')
            
    except (ValueError, IndexError):
        return "Mois inconnu"


def get_weekday_name(date_str: str, lang: str = "fr") -> str:
    """
    Retourne le nom du jour de la semaine
    
    Args:
        date_str (str): Date (YYYY-MM-DD)
        lang (str): Langue ("fr" ou "en")
        
    Returns:
        str: Nom du jour
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        weekday_num = date_obj.weekday()
        
        if lang == "fr":
            days_fr = [
                "Lundi", "Mardi", "Mercredi", "Jeudi", 
                "Vendredi", "Samedi", "Dimanche"
            ]
            return days_fr[weekday_num]
        else:
            return date_obj.strftime('%A')
            
    except (ValueError, IndexError):
        return "Jour inconnu"


def is_weekend(date_str: str) -> bool:
    """
    Vérifie si une date tombe un weekend
    
    Args:
        date_str (str): Date (YYYY-MM-DD)
        
    Returns:
        bool: True si weekend (samedi ou dimanche)
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.weekday() >= 5  # 5 = samedi, 6 = dimanche
    except ValueError:
        return False


def get_next_weekday(date_str: str, weekday: int) -> str:
    """
    Trouve la prochaine occurrence d'un jour de la semaine
    
    Args:
        date_str (str): Date de départ (YYYY-MM-DD)
        weekday (int): Jour de la semaine (0=lundi, 6=dimanche)
        
    Returns:
        str: Prochaine date du jour demandé
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        days_ahead = weekday - date_obj.weekday()
        
        if days_ahead <= 0:  # Le jour est déjà passé cette semaine
            days_ahead += 7
            
        next_date = date_obj + timedelta(days=days_ahead)
        return next_date.strftime('%Y-%m-%d')
        
    except ValueError:
        return date_str


def timestamp_to_unix(timestamp: str) -> Optional[int]:
    """
    Convertit un timestamp ISO en timestamp Unix
    
    Args:
        timestamp (str): Timestamp ISO
        
    Returns:
        Optional[int]: Timestamp Unix ou None si erreur
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return int(dt.timestamp())
    except (ValueError, TypeError):
        return None


def unix_to_timestamp(unix_timestamp: int) -> str:
    """
    Convertit un timestamp Unix en timestamp ISO
    
    Args:
        unix_timestamp (int): Timestamp Unix
        
    Returns:
        str: Timestamp ISO
    """
    try:
        dt = datetime.fromtimestamp(unix_timestamp)
        return dt.isoformat()
    except (ValueError, OSError):
        return get_current_timestamp()


def get_time_until_date(target_date: str) -> Optional[dict]:
    """
    Calcule le temps restant jusqu'à une date
    
    Args:
        target_date (str): Date cible (YYYY-MM-DD)
        
    Returns:
        Optional[dict]: Dictionnaire avec jours, heures, minutes ou None
    """
    try:
        target = datetime.strptime(target_date, '%Y-%m-%d')
        now = datetime.now()
        
        if target < now:
            return None  # Date passée
            
        diff = target - now
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'total_hours': days * 24 + hours
        }
        
    except ValueError:
        return None


def format_duration_human(minutes: int) -> str:
    """
    Formate une durée en format lisible
    
    Args:
        minutes (int): Durée en minutes
        
    Returns:
        str: Durée formatée (ex: "2h 30min")
    """
    try:
        if minutes < 60:
            return f"{minutes}min"
        
        hours, mins = divmod(minutes, 60)
        
        if mins == 0:
            return f"{hours}h"
        else:
            return f"{hours}h{mins:02d}min"
            
    except (TypeError, ValueError):
        return "0min"


def get_business_days_between(start_date: str, end_date: str) -> Optional[int]:
    """
    Calcule le nombre de jours ouvrables entre deux dates
    
    Args:
        start_date (str): Date de début (YYYY-MM-DD)
        end_date (str): Date de fin (YYYY-MM-DD)
        
    Returns:
        Optional[int]: Nombre de jours ouvrables ou None si erreur
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start > end:
            return 0
            
        business_days = 0
        current = start
        
        while current <= end:
            if current.weekday() < 5:  # Lundi à vendredi
                business_days += 1
            current += timedelta(days=1)
            
        return business_days
        
    except ValueError:
        return None