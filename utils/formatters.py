
from datetime import datetime
from typing import Optional, Union


def format_player_name(player) -> str:
    """
    Formate le nom complet d'un joueur
    
    Args:
        player: Objet joueur avec first_name et last_name
        
    Returns:
        str: Nom formaté "Prénom Nom"
    """
    try:
        if hasattr(player, 'first_name') and hasattr(player, 'last_name'):
            return f"{player.first_name} {player.last_name}"
        return str(player)
    except Exception:
        return "Joueur inconnu"


def format_score_display(score: Union[int, float]) -> str:
    """
    Formate l'affichage d'un score
    
    Args:
        score (Union[int, float]): Score à formater
        
    Returns:
        str: Score formaté
    """
    try:
        if score == int(score):
            return str(int(score))
        return f"{score:.1f}"
    except Exception:
        return "0"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formate un pourcentage
    
    Args:
        value (float): Valeur à formater (0-100)
        decimals (int): Nombre de décimales
        
    Returns:
        str: Pourcentage formaté avec %
    """
    try:
        return f"{value:.{decimals}f}%"
    except Exception:
        return "0.0%"


def format_date_display(date_str: str, input_format: str = "%Y-%m-%d", 
                       output_format: str = "%d/%m/%Y") -> str:
    """
    Formate une date pour l'affichage
    
    Args:
        date_str (str): Date en format string
        input_format (str): Format d'entrée
        output_format (str): Format de sortie
        
    Returns:
        str: Date formatée
    """
    try:
        if not date_str:
            return "Non définie"
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except Exception:
        return date_str


def format_tournament_status(tournament) -> str:
    """
    Formate le statut d'un tournoi
    
    Args:
        tournament: Objet tournoi
        
    Returns:
        str: Statut formaté
    """
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
    """
    Formate le résultat d'un match
    
    Args:
        match: Objet match avec scores
        
    Returns:
        str: Résultat formaté
    """
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
    """
    Formate une durée entre deux timestamps
    
    Args:
        start_time (str): Timestamp de début
        end_time (str): Timestamp de fin
        
    Returns:
        str: Durée formatée
    """
    try:
        if not start_time or not end_time:
            return "Durée inconnue"
            
        # Convertir les timestamps en datetime
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


def format_ranking_position(position: int) -> str:
    """
    Formate une position dans un classement
    
    Args:
        position (int): Position (1, 2, 3, etc.)
        
    Returns:
        str: Position formatée avec suffixe
    """
    try:
        if position == 1:
            return "1er"
        elif position == 2:
            return "2e"
        elif position == 3:
            return "3e"
        else:
            return f"{position}e"
    except Exception:
        return str(position)


def format_player_record(wins: int, draws: int, losses: int) -> str:
    """
    Formate le bilan d'un joueur
    
    Args:
        wins (int): Nombre de victoires
        draws (int): Nombre de nuls
        losses (int): Nombre de défaites
        
    Returns:
        str: Bilan formaté "V-N-D"
    """
    try:
        return f"{wins}-{draws}-{losses}"
    except Exception:
        return "0-0-0"


def format_large_number(number: Union[int, float]) -> str:
    """
    Formate un grand nombre avec séparateurs
    
    Args:
        number (Union[int, float]): Nombre à formater
        
    Returns:
        str: Nombre formaté avec espaces
    """
    try:
        if isinstance(number, float):
            return f"{number:,.2f}".replace(',', ' ')
        else:
            return f"{number:,}".replace(',', ' ')
    except Exception:
        return str(number)


def format_file_size(size_bytes: int) -> str:
    """
    Formate une taille de fichier en unités lisibles
    
    Args:
        size_bytes (int): Taille en octets
        
    Returns:
        str: Taille formatée (Ko, Mo, Go)
    """
    try:
        if size_bytes < 1024:
            return f"{size_bytes} o"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} Ko"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} Mo"
        else:
            return f"{size_bytes/(1024**3):.1f} Go"
    except Exception:
        return "0 o"


def format_time_ago(timestamp: str) -> str:
    """
    Formate un timestamp en "il y a X temps"
    
    Args:
        timestamp (str): Timestamp ISO
        
    Returns:
        str: Temps relatif formaté
    """
    try:
        past_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - past_time
        
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"il y a {days} jour{'s' if days > 1 else ''}"
        elif hours > 0:
            return f"il y a {hours} heure{'s' if hours > 1 else ''}"
        elif minutes > 0:
            return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "à l'instant"
    except Exception:
        return "Date inconnue"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Tronque un texte à une longueur maximale
    
    Args:
        text (str): Texte à tronquer
        max_length (int): Longueur maximale
        suffix (str): Suffixe à ajouter si tronqué
        
    Returns:
        str: Texte tronqué si nécessaire
    """
    try:
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    except Exception:
        return str(text)


def format_list_display(items: list, separator: str = ", ", 
                       max_items: int = 3, more_text: str = "et {} autres") -> str:
    """
    Formate une liste pour l'affichage
    
    Args:
        items (list): Liste d'éléments
        separator (str): Séparateur entre éléments
        max_items (int): Nombre maximum d'éléments à afficher
        more_text (str): Texte pour les éléments supplémentaires
        
    Returns:
        str: Liste formatée
    """
    try:
        if not items:
            return "Aucun élément"
            
        if len(items) <= max_items:
            return separator.join(str(item) for item in items)
        else:
            displayed_items = separator.join(str(item) for item in items[:max_items])
            remaining_count = len(items) - max_items
            return f"{displayed_items}{separator}{more_text.format(remaining_count)}"
    except Exception:
        return "Liste non disponible"


def format_table_cell(value: any, width: int, align: str = "left") -> str:
    """
    Formate une cellule de tableau avec alignement
    
    Args:
        value (any): Valeur à formater
        width (int): Largeur de la cellule
        align (str): Alignement (left, right, center)
        
    Returns:
        str: Cellule formatée
    """
    try:
        text = str(value)
        if len(text) > width:
            text = text[:width-3] + "..."
            
        if align == "right":
            return text.rjust(width)
        elif align == "center":
            return text.center(width)
        else:
            return text.ljust(width)
    except Exception:
        return " " * width


def format_currency(amount: float, currency: str = "€") -> str:
    """
    Formate un montant monétaire
    
    Args:
        amount (float): Montant
        currency (str): Symbole de devise
        
    Returns:
        str: Montant formaté
    """
    try:
        return f"{amount:.2f} {currency}"
    except Exception:
        return f"0.00 {currency}"


def format_yes_no(value: bool) -> str:
    """
    Formate une valeur booléenne en (oui/non)
    
    Args:
        value (bool): Valeur booléenne
        
    Returns:
        str: "Oui" ou "Non"
    """
    try:
        return "Oui" if value else "Non"
    except Exception:
        return "Non défini"