from datetime import datetime
from typing import Union


def format_player_name(player) -> str:
    try:
        if hasattr(player, 'first_name') and hasattr(player, 'last_name'):
            return f"{player.first_name} {player.last_name}"
        return str(player)
    except Exception:
        return "Joueur inconnu"


def format_score_display(score: Union[int, float]) -> str:
    try:
        if score == int(score):
            return str(int(score))
        return f"{score:.1f}"
    except Exception:
        return "0"


def format_percentage(value: float, decimals: int = 1) -> str:
    try:
        return f"{value:.{decimals}f}%"
    except Exception:
        return "0.0%"


def format_date_display(date_str: str, input_format: str = "%Y-%m-%d",
                        output_format: str = "%d/%m/%Y") -> str:
    try:
        if not date_str:
            return "Non définie"
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except Exception:
        return date_str


def format_tournament_status(tournament) -> str:
    try:
        if hasattr(tournament, 'is_finished') and tournament.is_finished():
            return "Terminé"
        elif hasattr(tournament, 'has_started') and tournament.has_started():
            return "En cours"
        else:
            return "Non commencé"
    except Exception:
        return "Statut inconnu"


def format_match_result(match) -> str:
    try:
        if not hasattr(match, 'is_finished') or not match.is_finished:
            return "Match en cours"

        p1_score = format_score_display(match.player1_score)
        p2_score = format_score_display(match.player2_score)
        p1_id = getattr(match, 'player1_national_id', 'Joueur 1')
        p2_id = getattr(match, 'player2_national_id', 'Joueur 2')

        return f"{p1_id} {p1_score}-{p2_score} {p2_id}"
    except Exception:
        return "Résultat non disponible"


def format_duration(start_time: str, end_time: str) -> str:
    try:
        if not start_time or not end_time:
            return "Durée inconnue"

        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        duration = end - start
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        if hours > 0:
            return f"{int(hours)}h{int(minutes):02d}min"
        else:
            return f"{int(minutes)}min"
    except Exception:
        return "Durée invalide"