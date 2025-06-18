#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helpers pour les tournois - Architecture MVC - 
Responsabilité : Logique complexe des tournois déportée des modèles
"""

import random
from typing import List, Tuple, Dict, Set
from collections import defaultdict


class TournamentPairingHelper:
    """
    Helper pour la génération des paires selon le système suisse
    Responsabilité : Algorithmes d'appariement pour les tournois
    """
    
    @staticmethod
    def generate_pairs_for_next_round(tournament) -> List[Tuple]:
        """
        Génère les paires pour le tour suivant selon le système suisse
        
        Args:
            tournament: Instance de Tournament
            
        Returns:
            List[Tuple]: Liste de paires (player1, player2)
            
        Raises:
            ValueError: Si impossible de générer des paires
        """
        if len(tournament.players) % 2 != 0:
            raise ValueError("Nombre impair de joueurs")
        
        if tournament.current_round == 0:
            # Premier tour : mélange aléatoire
            return TournamentPairingHelper._generate_first_round_pairs(tournament.players)
        else:
            # Tours suivants : système suisse
            return TournamentPairingHelper._generate_swiss_pairs(tournament)
    
    @staticmethod
    def _generate_first_round_pairs(players: List) -> List[Tuple]:
        """
        Génère les paires du premier tour (aléatoire)
        
        Args:
            players (List): Liste des joueurs
            
        Returns:
            List[Tuple]: Paires générées
        """
        players_copy = players.copy()
        random.shuffle(players_copy)
        
        pairs = []
        for i in range(0, len(players_copy), 2):
            pairs.append((players_copy[i], players_copy[i + 1]))
        
        return pairs
    
    @staticmethod
    def _generate_swiss_pairs(tournament) -> List[Tuple]:
        """
        Génère les paires selon le système suisse - 
        Algorithme : trier par score, éviter les rematches
        
        Args:
            tournament: Instance de Tournament
            
        Returns:
            List[Tuple]: Paires générées selon le système suisse
        """
        # : Trier les joueurs par score décroissant via tournament.get_player_score()
        sorted_players = sorted(
            tournament.players,
            key=lambda p: (-tournament.get_player_score(p.national_id), p.last_name, p.first_name)
        )
        
        pairs = []
        available_players = sorted_players.copy()
        
        # Générer les paires en évitant les rematches
        while len(available_players) >= 2:
            player1 = available_players.pop(0)
            
            # Chercher le premier adversaire qui n'a pas encore joué contre player1
            opponent_found = False
            for i, player2 in enumerate(available_players):
                if not TournamentPairingHelper._have_played_against(tournament, player1, player2):
                    pairs.append((player1, player2))
                    available_players.pop(i)
                    opponent_found = True
                    break
            
            # Si aucun adversaire valide trouvé, prendre le premier disponible
            if not opponent_found and available_players:
                player2 = available_players.pop(0)
                pairs.append((player1, player2))
        
        return pairs
    
    @staticmethod
    def _have_played_against(tournament, player1, player2) -> bool:
        """
        Vérifie si deux joueurs se sont déjà affrontés
        
        Args:
            tournament: Instance de Tournament
            player1: Premier joueur
            player2: Deuxième joueur
            
        Returns:
            bool: True s'ils se sont déjà affrontés
        """
        for round_obj in tournament.rounds:
            for match in round_obj.matches:
                if ((match.player1_national_id == player1.national_id and 
                     match.player2_national_id == player2.national_id) or
                    (match.player1_national_id == player2.national_id and 
                     match.player2_national_id == player1.national_id)):
                    return True
        return False
    
    @staticmethod
    def analyze_pairing_quality(tournament, pairs: List[Tuple]) -> Dict:
        """
        Analyse la qualité des appariements générés - 
        
        Args:
            tournament: Instance de Tournament
            pairs (List[Tuple]): Paires à analyser
            
        Returns:
            Dict: Métriques de qualité des appariements
        """
        total_pairs = len(pairs)
        rematches = 0
        score_differences = []
        
        for player1, player2 in pairs:
            # Compter les rematches
            if TournamentPairingHelper._have_played_against(tournament, player1, player2):
                rematches += 1
            
            # : Calculer les différences de score via tournament.get_player_score()
            player1_score = tournament.get_player_score(player1.national_id)
            player2_score = tournament.get_player_score(player2.national_id)
            score_diff = abs(player1_score - player2_score)
            score_differences.append(score_diff)
        
        avg_score_difference = sum(score_differences) / len(score_differences) if score_differences else 0
        
        return {
            'total_pairs': total_pairs,
            'rematches_count': rematches,
            'rematch_rate': (rematches / total_pairs * 100) if total_pairs > 0 else 0,
            'average_score_difference': avg_score_difference,
            'max_score_difference': max(score_differences) if score_differences else 0,
            'balanced_pairs': sum(1 for diff in score_differences if diff <= 1.0),
            'quality_rating': TournamentPairingHelper._calculate_quality_rating(rematches, total_pairs, avg_score_difference)
        }
    
    @staticmethod
    def _calculate_quality_rating(rematches: int, total_pairs: int, avg_score_diff: float) -> str:
        """Calcule une note qualitative des appariements"""
        if total_pairs == 0:
            return "N/A"
        
        rematch_penalty = (rematches / total_pairs) * 50  # Pénalité pour les rematches
        score_penalty = min(avg_score_diff * 10, 30)      # Pénalité pour les différences de score
        
        quality_score = 100 - rematch_penalty - score_penalty
        
        if quality_score >= 80:
            return "Excellent"
        elif quality_score >= 60:
            return "Bon"
        elif quality_score >= 40:
            return "Moyen"
        else:
            return "Faible"


class TournamentValidationHelper:
    """
    Helper pour la validation des tournois
    Responsabilité : Vérifications d'intégrité et de cohérence
    """
    
    @staticmethod
    def validate_tournament_state(tournament) -> List[str]:
        """
        Valide l'état complet d'un tournoi
        
        Args:
            tournament: Instance de Tournament
            
        Returns:
            List[str]: Liste des erreurs trouvées
        """
        errors = []
        
        # Validation du nombre de joueurs
        errors.extend(TournamentValidationHelper._validate_players(tournament))
        
        # Validation des tours
        errors.extend(TournamentValidationHelper._validate_rounds(tournament))
        
        # Validation de la cohérence générale
        errors.extend(TournamentValidationHelper._validate_consistency(tournament))
        
        return errors
    
    @staticmethod
    def _validate_players(tournament) -> List[str]:
        """Valide les joueurs du tournoi"""
        errors = []
        
        if len(tournament.players) < 2:
            errors.append("Au moins 2 joueurs requis")
        
        if len(tournament.players) % 2 != 0:
            errors.append("Le nombre de joueurs doit être pair")
        
        # Vérifier l'unicité des IDs
        seen_ids = set()
        for player in tournament.players:
            if player.national_id in seen_ids:
                errors.append(f"ID joueur dupliqué: {player.national_id}")
            seen_ids.add(player.national_id)
        
        return errors
    
    @staticmethod
    def _validate_rounds(tournament) -> List[str]:
        """Valide les tours du tournoi"""
        errors = []
        
        for i, round_obj in enumerate(tournament.rounds):
            round_number = i + 1
            
            # Vérifier que le tour a des matchs
            if not round_obj.matches:
                errors.append(f"Tour {round_number}: Aucun match")
                continue
            
            # Vérifier les doublons de joueurs dans le tour
            players_in_round = []
            for match in round_obj.matches:
                players_in_round.extend([match.player1_national_id, match.player2_national_id])
            
            seen_in_round = set()
            for player_id in players_in_round:
                if player_id in seen_in_round:
                    errors.append(f"Tour {round_number}: Joueur {player_id} joue plusieurs fois")
                seen_in_round.add(player_id)
            
            # Vérifier que tous les joueurs du tournoi participent
            tournament_player_ids = {p.national_id for p in tournament.players}
            round_player_ids = set(players_in_round)
            
            missing_players = tournament_player_ids - round_player_ids
            if missing_players:
                errors.append(f"Tour {round_number}: Joueurs manquants: {', '.join(missing_players)}")
            
            extra_players = round_player_ids - tournament_player_ids
            if extra_players:
                errors.append(f"Tour {round_number}: Joueurs non inscrits: {', '.join(extra_players)}")
        
        return errors
    
    @staticmethod
    def _validate_consistency(tournament) -> List[str]:
        """Valide la cohérence générale"""
        errors = []
        
        # Vérifier la cohérence entre current_round et nombre de tours
        if tournament.current_round != len(tournament.rounds):
            errors.append(f"Incohérence: current_round={tournament.current_round}, tours réels={len(tournament.rounds)}")
        
        # Vérifier que les tours terminés le sont vraiment
        for i, round_obj in enumerate(tournament.rounds):
            if round_obj.is_finished and not round_obj.all_matches_finished():
                errors.append(f"Tour {i+1}: Marqué terminé mais des matchs sont incomplets")
        
        # Vérifier l'ordre des tours
        if tournament.rounds:
            last_round = tournament.rounds[-1]
            if not last_round.is_finished and tournament.is_finished():
                errors.append("Tournoi marqué terminé mais le dernier tour n'est pas fini")
        
        return errors
    
    @staticmethod
    def validate_player_scores(tournament) -> List[str]:
        """
        Valide que les scores des joueurs correspondent aux résultats des matchs - 
        
        Args:
            tournament: Instance de Tournament
            
        Returns:
            List[str]: Erreurs de cohérence des scores
        """
        errors = []
        
        # Calculer les scores attendus basés sur les matchs
        expected_scores = defaultdict(float)
        
        for round_obj in tournament.rounds:
            for match in round_obj.get_finished_matches():
                expected_scores[match.player1_national_id] += match.player1_score
                expected_scores[match.player2_national_id] += match.player2_score
        
        # : Comparer avec les scores du tournoi
        for player in tournament.players:
            expected = expected_scores.get(player.national_id, 0.0)
            actual = tournament.get_player_score(player.national_id)
            
            if abs(expected - actual) > 0.001:  # Tolérance pour les flottants
                errors.append(
                    f"Joueur {player.national_id}: score actuel {actual}, "
                    f"score attendu {expected}"
                )
        
        return errors


class TournamentStatisticsHelper:
    """
    Helper pour les calculs statistiques des tournois
    Responsabilité : Métriques et analyses de performance
    """
    
    @staticmethod
    def calculate_tournament_statistics(tournament) -> Dict:
        """
        Calcule les statistiques complètes d'un tournoi
        
        Args:
            tournament: Instance de Tournament
            
        Returns:
            Dict: Statistiques détaillées
        """
        stats = {
            'basic_info': TournamentStatisticsHelper._get_basic_info(tournament),
            'participation': TournamentStatisticsHelper._get_participation_stats(tournament),
            'match_results': TournamentStatisticsHelper._get_match_results(tournament),
            'performance': TournamentStatisticsHelper._get_performance_stats(tournament),
            'progression': TournamentStatisticsHelper._get_progression_stats(tournament)
        }
        
        return stats
    
    @staticmethod
    def _get_basic_info(tournament) -> Dict:
        """Informations de base du tournoi"""
        total_matches = sum(len(round_obj.matches) for round_obj in tournament.rounds)
        finished_matches = sum(len(round_obj.get_finished_matches()) for round_obj in tournament.rounds)
        
        return {
            'name': tournament.name,
            'location': tournament.location,
            'players_count': len(tournament.players),
            'rounds_planned': tournament.number_of_rounds,
            'rounds_played': len(tournament.rounds),
            'total_matches': total_matches,
            'finished_matches': finished_matches,
            'completion_rate': (finished_matches / total_matches * 100) if total_matches > 0 else 0,
            'is_finished': tournament.is_finished(),
            'status': 'Terminé' if tournament.is_finished() else ('En cours' if tournament.has_started() else 'Non commencé')
        }
    
    @staticmethod
    def _get_participation_stats(tournament) -> Dict:
        """Statistiques de participation"""
        if not tournament.rounds:
            return {'active_players': 0, 'participation_rate': 0}
        
        # Compter les joueurs actifs (qui ont joué au moins un match)
        active_players = set()
        for round_obj in tournament.rounds:
            for match in round_obj.matches:
                active_players.add(match.player1_national_id)
                active_players.add(match.player2_national_id)
        
        return {
            'registered_players': len(tournament.players),
            'active_players': len(active_players),
            'participation_rate': (len(active_players) / len(tournament.players) * 100) if tournament.players else 0
        }
    
    @staticmethod
    def _get_match_results(tournament) -> Dict:
        """Statistiques des résultats de matchs"""
        wins = 0
        draws = 0
        total_finished = 0
        
        for round_obj in tournament.rounds:
            for match in round_obj.get_finished_matches():
                total_finished += 1
                if match.is_draw():
                    draws += 1
                else:
                    wins += 1
        
        return {
            'total_finished_matches': total_finished,
            'decisive_games': wins,
            'draws': draws,
            'draw_rate': (draws / total_finished * 100) if total_finished > 0 else 0,
            'decisive_rate': (wins / total_finished * 100) if total_finished > 0 else 0
        }
    
    @staticmethod
    def _get_performance_stats(tournament) -> Dict:
        """Statistiques de performance des joueurs - """
        if not tournament.players:
            return {}
        
        # : Récupérer les scores via tournament.get_player_score()
        scores = [tournament.get_player_score(p.national_id) for p in tournament.players]
        scores.sort(reverse=True)
        
        # Calculer les métriques
        total_score = sum(scores)
        avg_score = total_score / len(scores)
        
        # Trouver les joueurs de tête
        max_score = max(scores) if scores else 0
        leaders = [p for p in tournament.players if tournament.get_player_score(p.national_id) == max_score]
        
        # Distribution des scores
        score_distribution = defaultdict(int)
        for score in scores:
            score_distribution[score] += 1
        
        return {
            'average_score': avg_score,
            'highest_score': max_score,
            'lowest_score': min(scores) if scores else 0,
            'leaders_count': len(leaders),
            'score_spread': max_score - min(scores) if scores else 0,
            'score_distribution': dict(score_distribution)
        }
    
    @staticmethod
    def _get_progression_stats(tournament) -> Dict:
        """Statistiques de progression par tour"""
        if not tournament.rounds:
            return {'rounds_data': []}
        
        rounds_data = []
        
        for i, round_obj in enumerate(tournament.rounds):
            round_stats = {
                'round_number': i + 1,
                'round_name': round_obj.name,
                'matches_count': len(round_obj.matches),
                'finished_matches': len(round_obj.get_finished_matches()),
                'completion_rate': round_obj.get_completion_percentage(),
                'duration_minutes': round_obj.get_duration_minutes(),
                'is_finished': round_obj.is_finished
            }
            
            # Statistiques des résultats du tour
            wins = sum(1 for match in round_obj.get_finished_matches() if not match.is_draw())
            draws = sum(1 for match in round_obj.get_finished_matches() if match.is_draw())
            
            round_stats.update({
                'wins': wins,
                'draws': draws,
                'draw_rate': (draws / len(round_obj.get_finished_matches()) * 100) if round_obj.get_finished_matches() else 0
            })
            
            rounds_data.append(round_stats)
        
        return {'rounds_data': rounds_data}
    
    @staticmethod
    def calculate_player_performance_in_tournament(tournament, player_id: str) -> Dict:
        """
        Calcule les statistiques de performance d'un joueur spécifique - 
        
        Args:
            tournament: Instance de Tournament
            player_id (str): ID du joueur
            
        Returns:
            Dict: Statistiques du joueur dans ce tournoi
        """
        player = tournament.get_player_by_id(player_id)
        if not player:
            return {'error': 'Joueur non trouvé'}
        
        matches_played = []
        total_wins = 0
        total_draws = 0
        total_losses = 0
        opponents = []
        
        for round_obj in tournament.rounds:
            for match in round_obj.matches:
                if match.involves_player(player_id):
                    matches_played.append(match)
                    
                    if match.is_finished:
                        opponent_id = match.get_opponent_id(player_id)
                        opponents.append(opponent_id)
                        
                        player_score = match.get_score_for_player(player_id)
                        if player_score == 1.0:
                            total_wins += 1
                        elif player_score == 0.5:
                            total_draws += 1
                        else:
                            total_losses += 1
        
        total_games = total_wins + total_draws + total_losses
        
        return {
            'player_name': player.get_full_name(),
            'current_score': tournament.get_player_score(player.national_id),  # 
            'matches_played': len(matches_played),
            'finished_games': total_games,
            'wins': total_wins,
            'draws': total_draws,
            'losses': total_losses,
            'win_rate': (total_wins / total_games * 100) if total_games > 0 else 0,
            'draw_rate': (total_draws / total_games * 100) if total_games > 0 else 0,
            'performance_rating': (total_wins + total_draws * 0.5) / total_games * 100 if total_games > 0 else 0,
            'opponents_faced': list(set(opponents))
        }
    
    @staticmethod
    def analyze_tournament_competitiveness(tournament) -> Dict:
        """
        Analyse le niveau de compétitivité du tournoi - 
        
        Args:
            tournament: Instance de Tournament
            
        Returns:
            Dict: Métriques de compétitivité
        """
        if not tournament.players or len(tournament.players) < 2:
            return {'competitiveness': 'Insufficient data'}
        
        # : Récupérer les scores via tournament.get_player_score()
        scores = [tournament.get_player_score(p.national_id) for p in tournament.players]
        scores.sort(reverse=True)
        
        # Calculer l'écart-type des scores
        avg_score = sum(scores) / len(scores)
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Analyser la distribution
        max_score = max(scores)
        min_score = min(scores)
        score_range = max_score - min_score
        
        # Compter les joueurs dans différentes tranches
        top_quarter = len([s for s in scores if s >= avg_score + std_dev])
        bottom_quarter = len([s for s in scores if s <= avg_score - std_dev])
        
        # Déterminer le niveau de compétitivité
        if std_dev < 1.0 and score_range < 2.0:
            competitiveness = "Très équilibré"
        elif std_dev < 2.0 and score_range < 4.0:
            competitiveness = "Équilibré"
        elif std_dev < 3.0:
            competitiveness = "Modérément équilibré"
        else:
            competitiveness = "Déséquilibré"
        
        return {
            'competitiveness': competitiveness,
            'score_standard_deviation': std_dev,
            'score_range': score_range,
            'average_score': avg_score,
            'players_above_average': len([s for s in scores if s > avg_score]),
            'players_below_average': len([s for s in scores if s < avg_score]),
            'top_performers': top_quarter,
            'bottom_performers': bottom_quarter,
            'coefficient_variation': (std_dev / avg_score * 100) if avg_score > 0 else 0
        }