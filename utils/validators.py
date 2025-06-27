import re
from datetime import datetime, timedelta
from typing import Tuple


def validate_chess_id(chess_id: str) -> bool:
    if not chess_id or not isinstance(chess_id, str):
        return False

    chess_id = chess_id.strip().upper()

    pattern = r'^[A-Z]{2}\d{5}$'
    return bool(re.match(pattern, chess_id))


def validate_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False

    name = name.strip()

    if len(name) < 2:
        return False

    pattern = r"^[a-zA-ZÀ-ÿ\s\-']+$"
    return bool(re.match(pattern, name))


def validate_date_format(date_str: str) -> bool:
    if not date_str or not isinstance(date_str, str):
        return False

    try:
        datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_score(score: float) -> bool:
    if not isinstance(score, (int, float)):
        return False

    return score in [0, 0.5, 1, 0.0, 1.0]


def validate_tournament_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False

    name = name.strip()

    if len(name) < 3 or len(name) > 100:
        return False

    pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-'\.]+$"
    return bool(re.match(pattern, name))


def validate_location(location: str) -> bool:
    if not location or not isinstance(location, str):
        return False

    location = location.strip()

    if len(location) < 2 or len(location) > 200:
        return False

    pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-',\.]+$"
    return bool(re.match(pattern, location))


def validate_date_range(start_date: str, end_date: str) -> bool:
    if (not validate_date_format(start_date) or
            not validate_date_format(end_date)):
        return False

    try:
        start = datetime.strptime(start_date.strip(), '%Y-%m-%d')
        end = datetime.strptime(end_date.strip(), '%Y-%m-%d')
        return end >= start
    except ValueError:
        return False


def validate_tournament_dates(start_date: str,
                              end_date: str) -> Tuple[bool, str]:
    if not validate_date_format(start_date):
        return False, "Format de date de début invalide (YYYY-MM-DD)"

    if not validate_date_format(end_date):
        return False, "Format de date de fin invalide (YYYY-MM-DD)"

    if not validate_date_range(start_date, end_date):
        return (False, "La date de fin doit être postérieure ou égale "
                "à la date de début")

    try:
        start = datetime.strptime(start_date.strip(), '%Y-%m-%d')
        today = datetime.now()

        if start < today - timedelta(days=365):
            return (False, "La date de début ne peut pas être "
                    "antérieure à 1 an")

    except ValueError:
        pass

    return True, ""
