from datetime import datetime
from typing import Optional


def get_current_timestamp() -> str:
    return datetime.now().isoformat()


def calculate_age(birthdate: str,
                  reference_date: Optional[str] = None) -> Optional[int]:
    try:
        birth = datetime.strptime(birthdate, '%Y-%m-%d')

        if reference_date:
            ref = datetime.strptime(reference_date, '%Y-%m-%d')
        else:
            ref = datetime.now()

        age = ref.year - birth.year

        if (ref.month, ref.day) < (birth.month, birth.day):
            age -= 1

        return age if age >= 0 else None

    except ValueError:
        return None


def calculate_duration_minutes(start_timestamp: str,
                               end_timestamp: str) -> Optional[int]:
    try:
        start = datetime.fromisoformat(start_timestamp)
        end = datetime.fromisoformat(end_timestamp)

        duration = end - start
        return int(duration.total_seconds() / 60)

    except (ValueError, TypeError):
        return None


def format_duration_human(minutes: int) -> str:
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