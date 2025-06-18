#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helpers pour les matchs - Architecture MVC
Responsabilité : Logique complexe des matchs déportée des modèles
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter


class MatchAnalysisHelper:
    """
    Helper pour l'analyse des matchs
    Responsabilité : Analyses et statistiques des matchs individuels
    """
    
    @staticmethod
    def analyze_match_result(match) -> Dict:
        """
        Analyse détaillée d'un résultat de match
        
        Args:
            match: Instance de Match
            
        Returns:
            Dict: Analyse complète du match
        """
        if not match.is_finished:
            return {
                'status': 'unfinished',
                'players': [match.player1_national_id, match.player2_national_id],
                'progress': 'En cours'
            }
        
        analysis = {
            'status': 'finished',
            'result_type': 'draw' if match.is_draw() else 'decisive',
            'winner_id': match.get_winner_id(),
            'loser_id': match.get_loser_id(),
            'scores': {
                match.player1_national_id: match.player1_score,
                match.player2_national_id: match.player2_score
            },
            'match_summary': MatchAnalysisHelper._get_match_summary(match)
        }
        
        return analysis
    
    @staticmethod
    def _get_match_summary(match) -> str:
        """Génère un résumé textuel du match"""
        if match.is_draw():
            return "Match nul"
        
        winner_id = match.get_winner_id()
        loser_id = match.get_loser_id()
        
        if winner_id == match.player1_national_id:
            winner_score = match.player1_score
            loser_score = match.player2_score
        else:
            winner_score = match.player2_score
            loser_score = match.player1_score
        
        if winner_score == 1.0 and loser_score == 0.0:
            return f"Victoire nette de {winner_id}"
        else:
            return f"Victoire de {winner_id} ({winner_score}-{loser_score})"
    
    @staticmethod
    def get_head_to_head_summary(matches: List, player1_id: str, player2_id: str) -> Dict:
        """
        Résumé des confrontations entre deux joueurs
        
        Args:
            matches (List): Liste des matchs
            player1_id (str): ID du premier joueur
            player2_id (str): ID du deuxième joueur
            
        Returns:
            Dict: Résumé détaillé des confrontations
        """
        relevant_matches = [
            match for match in matches
            if match.involves_player(player1_id) and match.involves_player(player2_id) and match.is_finished
        ]
        
        player1_wins = 0
        player2_wins = 0
        draws = 0
        player1_total_score = 0.0
        player2_total_score = 0.0
        
        match_details = []
        
        for match in relevant_matches:
            winner = match.get_winner_id()
            player1_score = match.get_score_for_player(player1_id)
            player2_score = match.get_score_for_player(player2_id)
            
            player1_total_score += player1_score
            player2_total_score += player2_score
            
            if winner == player1_id:
                player1_wins += 1
                result = "Victoire P1"
            elif winner == player2_id:
                player2_wins += 1
                result = "Victoire P2"
            else:
                draws += 1
                result = "Nul"
            
            match_details.append({
                'player1_score': player1_score,
                'player2_score': player2_score,
                'result': result,
                'match_info': match
            })
        
        total_matches = len(relevant_matches)
        
        return {
            'total_matches': total_matches,
            'player1_wins': player1_wins,
            'player2_wins': player2_wins,
            'draws': draws,
            'player1_win_rate': (player1_wins / total_matches * 100) if total_matches > 0 else 0,
            'player2_win_rate': (player2_wins / total_matches * 100) if total_matches > 0 else 0,
            'draw_rate': (draws / total_matches * 100) if total_matches > 0 else 0,
            'player1_total_score': player1_total_score,
            'player2_total_score': player2_total_score,
            'player1_average_score': player1_total_score / total_matches if total_matches > 0 else 0,
            'player2_average_score': player2_total_score / total_matches if total_matches > 0 else 0,
            'matches_history': match_details,
            'series_leader': MatchAnalysisHelper._determine_series_leader(player1_wins, player2_wins, player1_id, player2_id)
        }
    
    @staticmethod
    def _determine_series_leader(p1_wins: int, p2_wins: int, p1_id: str, p2_id: str) -> Dict:
        """Détermine qui mène la série"""
        if p1_wins > p2_wins:
            return {'leader': p1_id, 'lead': p1_wins - p2_wins, 'status': 'dominance'}
        elif p2_wins > p1_wins:
            return {'leader': p2_id, 'lead': p2_wins - p1_wins, 'status': 'dominance'}
        else:
            return {'leader': None, 'lead': 0, 'status': 'tied'}
    
    @staticmethod
    def analyze_match_patterns(matches: List) -> Dict:
        """
        Analyse les patterns généraux dans une liste de matchs
        
        Args:
            matches (List): Liste des matchs à analyser
            
        Returns:
            Dict: Analyse des patterns
        """
        if not matches:
            return {'error': 'Aucun match à analyser'}
        
        finished_matches = [m for m in matches if m.is_finished]
        
        if not finished_matches:
            return {'error': 'Aucun match terminé'}
        
        # Compter les types de résultats
        decisive_games = 0
        draws = 0
        whitewashes = 0  # 1-0 scores
        
        score_distribution = Counter()
        
        for match in finished_matches:
            if match.is_draw():
                draws += 1
                score_distribution['0.5-0.5'] += 1
            else:
                decisive_games += 1
                winner_score = max(match.player1_score, match.player2_score)
                loser_score = min(match.player1_score, match.player2_score)
                
                if winner_score == 1.0 and loser_score == 0.0:
                    whitewashes += 1
                    score_distribution['1-0'] += 1
                else:
                    score_distribution[f'{winner_score}-{loser_score}'] += 1
        
        total_finished = len(finished_matches)
        
        return {
            'total_matches': len(matches),
            'finished_matches': total_finished,
            'completion_rate': (total_finished / len(matches) * 100),
            'decisive_games': decisive_games,
            'draws': draws,
            'whitewashes': whitewashes,
            'draw_rate': (draws / total_finished * 100),
            'decisive_rate': (decisive_games / total_finished * 100),
            'whitewash_rate': (whitewashes / total_finished * 100),
            'score_distribution': dict(score_distribution),
            'competitiveness': MatchAnalysisHelper._assess_competitiveness(draws, decisive_games, whitewashes)
        }
    
    @staticmethod
    def _assess_competitiveness(draws: int, decisive: int, whitewashes: int) -> str:
        """Évalue le niveau de compétitivité"""
        total = draws + decisive
        if total == 0:
            return "Aucune donnée"
        
        draw_rate = draws / total
        whitewash_rate = whitewashes / total
        
        if draw_rate > 0.4:
            return "Très équilibré (beaucoup de nuls)"
        elif draw_rate > 0.25 and whitewash_rate < 0.3:
            return "Équilibré"
        elif whitewash_rate > 0.6:
            return "Déséquilibré (beaucoup de victoires nettes)"
        else:
            return "Modérément équilibré"


class MatchStatisticsHelper:
    """
    Helper pour les statistiques avancées des matchs
    Responsabilité : Calculs statistiques complexes
    """
    
    @staticmethod
    def calculate_player_match_statistics(matches: List, player_id: str) -> Dict:
        """
        Calcule les statistiques complètes d'un joueur sur une série de matchs
        
        Args:
            matches (List): Liste des matchs
            player_id (str): ID du joueur
            
        Returns:
            Dict: Statistiques détaillées du joueur
        """
        player_matches = [m for m in matches if m.involves_player(player_id) and m.is_finished]
        
        if not player_matches:
            return {'error': 'Aucun match trouvé pour ce joueur'}
        
        wins = 0
        draws = 0
        losses = 0
        total_score = 0.0
        opponents = []
        performance_by_opponent = defaultdict(lambda: {'wins': 0, 'draws': 0, 'losses': 0, 'total_score': 0.0, 'matches': 0})
        
        for match in player_matches:
            opponent_id = match.get_opponent_id(player_id)
            player_score = match.get_score_for_player(player_id)
            
            opponents.append(opponent_id)
            total_score += player_score
            
            # Mettre à jour les statistiques générales
            if player_score == 1.0:
                wins += 1
                performance_by_opponent[opponent_id]['wins'] += 1
            elif player_score == 0.5:
                draws += 1
                performance_by_opponent[opponent_id]['draws'] += 1
            else:
                losses += 1
                performance_by_opponent[opponent_id]['losses'] += 1
            
            performance_by_opponent[opponent_id]['total_score'] += player_score
            performance_by_opponent[opponent_id]['matches'] += 1
        
        total_games = len(player_matches)
        unique_opponents = len(set(opponents))
        
        # Calculer les moyennes
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        draw_rate = (draws / total_games * 100) if total_games > 0 else 0
        loss_rate = (losses / total_games * 100) if total_games > 0 else 0
        average_score = total_score / total_games if total_games > 0 else 0
        
        # Identifier les adversaires les plus fréquents
        opponent_frequency = Counter(opponents)
        most_frequent_opponents = opponent_frequency.most_common(5)
        
        # Calculer la performance contre chaque adversaire
        opponent_stats = {}
        for opp_id, stats in performance_by_opponent.items():
            if stats['matches'] > 0:
                opponent_stats[opp_id] = {
                    'matches': stats['matches'],
                    'wins': stats['wins'],
                    'draws': stats['draws'],
                    'losses': stats['losses'],
                    'win_rate': (stats['wins'] / stats['matches'] * 100),
                    'average_score': stats['total_score'] / stats['matches']
                }
        
        return {
            'total_matches': total_games,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'total_score': total_score,
            'win_rate': win_rate,
            'draw_rate': draw_rate,
            'loss_rate': loss_rate,
            'average_score_per_game': average_score,
            'unique_opponents': unique_opponents,
            'most_frequent_opponents': most_frequent_opponents,
            'performance_by_opponent': opponent_stats,
            'performance_rating': MatchStatisticsHelper._calculate_performance_rating(win_rate, draw_rate),
            'consistency': MatchStatisticsHelper._calculate_consistency(player_matches, player_id)
        }
    
    @staticmethod
    def _calculate_performance_rating(win_rate: float, draw_rate: float) -> Dict:
        """Calcule un rating de performance"""
        rating = win_rate + (draw_rate * 0.5)
        
        if rating >= 80:
            level = "Excellent"
        elif rating >= 65:
            level = "Très bon"
        elif rating >= 50:
            level = "Bon"
        elif rating >= 35:
            level = "Moyen"
        else:
            level = "Faible"
        
        return {
            'rating': rating,
            'level': level
        }
    
    @staticmethod
    def _calculate_consistency(matches: List, player_id: str) -> Dict:
        """Calcule la régularité des performances"""
        scores = [match.get_score_for_player(player_id) for match in matches]
        
        if len(scores) < 2:
            return {'consistency_rating': 'N/A', 'variance': 0}
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_deviation = variance ** 0.5
        
        # Plus l'écart-type est faible, plus le joueur est régulier
        consistency_rating = max(0, 100 - (std_deviation * 200))  # Normaliser sur 100
        
        if consistency_rating >= 80:
            level = "Très régulier"
        elif consistency_rating >= 60:
            level = "Régulier"
        elif consistency_rating >= 40:
            level = "Irrégulier"
        else:
            level = "Très irrégulier"
        
        return {
            'consistency_rating': consistency_rating,
            'level': level,
            'variance': variance,
            'standard_deviation': std_deviation
        }
    
    @staticmethod
    def analyze_score_patterns(matches: List) -> Dict:
        """
        Analyse les patterns de scores dans les matchs
        
        Args:
            matches (List): Liste des matchs
            
        Returns:
            Dict: Analyse des patterns de scores
        """
        finished_matches = [m for m in matches if m.is_finished]
        
        if not finished_matches:
            return {'error': 'Aucun match terminé'}
        
        score_patterns = {
            '1-0': 0,      # Victoire nette
            '0.5-0.5': 0,  # Match nul
            'other': 0     # Autres (normalement inexistant aux échecs)
        }
        
        all_scores = []
        winner_margins = []
        
        for match in finished_matches:
            score1 = match.player1_score
            score2 = match.player2_score
            all_scores.extend([score1, score2])
            
            if match.is_draw():
                score_patterns['0.5-0.5'] += 1
            elif (score1 == 1.0 and score2 == 0.0) or (score1 == 0.0 and score2 == 1.0):
                score_patterns['1-0'] += 1
                winner_margins.append(1.0)
            else:
                score_patterns['other'] += 1
                winner_margins.append(abs(score1 - score2))
        
        # Calculer les statistiques
        total_finished = len(finished_matches)
        average_margin = sum(winner_margins) / len(winner_margins) if winner_margins else 0
        
        return {
            'total_analyzed': total_finished,
            'score_patterns': score_patterns,
            'pattern_percentages': {
                pattern: (count / total_finished * 100) 
                for pattern, count in score_patterns.items()
            },
            'average_winning_margin': average_margin,
            'competitiveness_indicator': 'High' if score_patterns['0.5-0.5'] > score_patterns['1-0'] * 0.8 else 'Medium'
        }