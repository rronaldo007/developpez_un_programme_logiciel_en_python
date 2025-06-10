from collections import defaultdict, Counter
from controllers.player_controller import PlayerController
from controllers.tournament_controller import TournamentController


class StatisticsController:
    """Contrôleur pour calculer et gérer les statistiques"""
    
    @staticmethod
    def get_player_statistics(national_id):
        """Calcule les statistiques d'un joueur"""
        player = PlayerController.get_player(national_id)
        if not player:
            return None
        
        tournaments = TournamentController.get_all_tournaments()
        
        stats = {
            "player_name": f"{player.first_name} {player.last_name}",
            "national_id": national_id,
            "tournaments_played": 0,
            "tournaments_won": 0,
            "tournaments_podium": 0,  # Top 3
            "total_matches": 0,
            "matches_won": 0,
            "matches_drawn": 0,
            "matches_lost": 0,
            "total_points": 0.0,
            "best_score": 0.0,
            "worst_score": 0.0,
            "average_score": 0.0,
            "win_rate": 0.0,
            "tournaments_details": []
        }
        
        tournament_scores = []
        
        for tournament in tournaments:
            # Vérifier si le joueur a participé
            tournament_player = None
            for p in tournament.players:
                if p.national_id == national_id:
                    tournament_player = p
                    break
            
            if not tournament_player:
                continue
            
            stats["tournaments_played"] += 1
            tournament_scores.append(tournament_player.score)
            stats["total_points"] += tournament_player.score
            
            # Position dans le tournoi
            sorted_players = sorted(tournament.players, key=lambda p: p.score, reverse=True)
            position = next((i+1 for i, p in enumerate(sorted_players) if p.national_id == national_id), 0)
            
            if position == 1:
                stats["tournaments_won"] += 1
            if position <= 3:
                stats["tournaments_podium"] += 1
            
            # Détails du tournoi
            stats["tournaments_details"].append({
                "name": tournament.name,
                "score": tournament_player.score,
                "position": position,
                "total_players": len(tournament.players),
                "date": tournament.start_date
            })
            
            # Compter les matchs
            for round_obj in tournament.rounds:
                for match in round_obj.matches:
                    if national_id in [match.player1_national_id, match.player2_national_id]:
                        if match.is_finished:
                            stats["total_matches"] += 1
                            
                            if national_id == match.player1_national_id:
                                player_score = match.player1_score
                            else:
                                player_score = match.player2_score
                            
                            if player_score == 1.0:
                                stats["matches_won"] += 1
                            elif player_score == 0.5:
                                stats["matches_drawn"] += 1
                            else:
                                stats["matches_lost"] += 1
        
        # Calculer les moyennes
        if tournament_scores:
            stats["best_score"] = max(tournament_scores)
            stats["worst_score"] = min(tournament_scores)
            stats["average_score"] = sum(tournament_scores) / len(tournament_scores)
        
        if stats["total_matches"] > 0:
            stats["win_rate"] = (stats["matches_won"] / stats["total_matches"]) * 100
        
        return stats
    
    @staticmethod
    def get_tournament_statistics(tournament_id):
        """Calcule les statistiques d'un tournoi"""
        tournament = TournamentController.get_tournament(tournament_id)
        if not tournament:
            return None
        
        stats = {
            "tournament_name": tournament.name,
            "location": tournament.location,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
            "total_players": len(tournament.players),
            "total_rounds": len(tournament.rounds),
            "total_matches": 0,
            "completed_matches": 0,
            "average_score": 0.0,
            "highest_score": 0.0,
            "lowest_score": 0.0,
            "winner_name": "",
            "winner_score": 0.0,
            "completion_rate": 0.0,
            "players_ranking": []
        }
        
        # Compter les matchs
        for round_obj in tournament.rounds:
            stats["total_matches"] += len(round_obj.matches)
            for match in round_obj.matches:
                if match.is_finished:
                    stats["completed_matches"] += 1
        
        # Statistiques des scores
        if tournament.players:
            scores = [p.score for p in tournament.players]
            stats["average_score"] = sum(scores) / len(scores)
            stats["highest_score"] = max(scores)
            stats["lowest_score"] = min(scores)
            
            # Gagnant
            winner = max(tournament.players, key=lambda p: p.score)
            stats["winner_name"] = f"{winner.first_name} {winner.last_name}"
            stats["winner_score"] = winner.score
            
            # Classement
            sorted_players = sorted(tournament.players, key=lambda p: p.score, reverse=True)
            stats["players_ranking"] = [
                {
                    "position": i+1,
                    "name": f"{p.first_name} {p.last_name}",
                    "score": p.score
                }
                for i, p in enumerate(sorted_players)
            ]
        
        # Taux de completion
        if stats["total_matches"] > 0:
            stats["completion_rate"] = (stats["completed_matches"] / stats["total_matches"]) * 100
        
        return stats
    
    @staticmethod
    def get_global_statistics():
        """Calcule les statistiques globales"""
        all_players = PlayerController.get_all_players()
        tournaments = TournamentController.get_all_tournaments()
        
        stats = {
            "total_players": len(all_players),
            "total_tournaments": len(tournaments),
            "completed_tournaments": 0,
            "total_matches": 0,
            "total_rounds": 0,
            "most_active_player": "",
            "most_successful_player": "",
            "most_popular_location": "",
            "average_players_per_tournament": 0.0,
            "recent_tournaments": []
        }
        
        if not tournaments:
            return stats
        
        # Compter tournois terminés et matchs
        locations = []
        players_per_tournament = []
        player_participation = defaultdict(int)
        player_wins = defaultdict(int)
        
        for tournament in tournaments:
            if tournament.current_round >= tournament.number_of_rounds:
                stats["completed_tournaments"] += 1
            
            stats["total_rounds"] += len(tournament.rounds)
            locations.append(tournament.location)
            players_per_tournament.append(len(tournament.players))
            
            # Compter participations
            for player in tournament.players:
                player_name = f"{player.first_name} {player.last_name}"
                player_participation[player_name] += 1
            
            # Compter victoires
            if tournament.current_round >= tournament.number_of_rounds and tournament.players:
                winner = max(tournament.players, key=lambda p: p.score)
                winner_name = f"{winner.first_name} {winner.last_name}"
                player_wins[winner_name] += 1
            
            # Compter matchs
            for round_obj in tournament.rounds:
                for match in round_obj.matches:
                    if match.is_finished:
                        stats["total_matches"] += 1
        
        # Calculer les moyennes
        if players_per_tournament:
            stats["average_players_per_tournament"] = sum(players_per_tournament) / len(players_per_tournament)
        
        # Joueur le plus actif
        if player_participation:
            stats["most_active_player"] = max(player_participation, key=player_participation.get)
        
        # Joueur le plus performant
        if player_wins:
            stats["most_successful_player"] = max(player_wins, key=player_wins.get)
        
        # Lieu le plus populaire
        if locations:
            location_counter = Counter(locations)
            stats["most_popular_location"] = location_counter.most_common(1)[0][0]
        
        # Tournois récents
        recent_tournaments = sorted(tournaments, key=lambda t: t.start_date, reverse=True)[:5]
        stats["recent_tournaments"] = [
            {
                "name": t.name,
                "date": t.start_date,
                "players": len(t.players),
                "status": "Terminé" if t.current_round >= t.number_of_rounds else "En cours"
            }
            for t in recent_tournaments
        ]
        
        return stats
    
    @staticmethod
    def get_top_players():
        """Calcule le classement des meilleurs joueurs"""
        all_players = PlayerController.get_all_players()
        tournaments = TournamentController.get_all_tournaments()
        
        player_stats = {}
        
        # Initialiser les stats pour chaque joueur
        for player in all_players:
            player_stats[player.national_id] = {
                "name": f"{player.first_name} {player.last_name}",
                "tournaments_played": 0,
                "tournaments_won": 0,
                "total_points": 0.0,
                "total_matches": 0,
                "matches_won": 0,
                "win_rate": 0.0,
                "average_score": 0.0
            }
        
        # Calculer les statistiques
        for tournament in tournaments:
            for tournament_player in tournament.players:
                if tournament_player.national_id in player_stats:
                    stats = player_stats[tournament_player.national_id]
                    stats["tournaments_played"] += 1
                    stats["total_points"] += tournament_player.score
                    
                    # Vérifier victoire
                    if tournament.current_round >= tournament.number_of_rounds:
                        winner = max(tournament.players, key=lambda p: p.score)
                        if winner.national_id == tournament_player.national_id:
                            stats["tournaments_won"] += 1
                    
                    # Compter matchs
                    for round_obj in tournament.rounds:
                        for match in round_obj.matches:
                            if tournament_player.national_id in [match.player1_national_id, match.player2_national_id]:
                                if match.is_finished:
                                    stats["total_matches"] += 1
                                    player_score = (match.player1_score if tournament_player.national_id == match.player1_national_id 
                                                   else match.player2_score)
                                    if player_score == 1.0:
                                        stats["matches_won"] += 1
        
        # Calculer moyennes et filtrer joueurs actifs
        active_players = []
        for stats in player_stats.values():
            if stats["tournaments_played"] > 0:
                stats["average_score"] = stats["total_points"] / stats["tournaments_played"]
                if stats["total_matches"] > 0:
                    stats["win_rate"] = (stats["matches_won"] / stats["total_matches"]) * 100
                active_players.append(stats)
        
        return {
            "by_tournaments_won": sorted(active_players, key=lambda x: x["tournaments_won"], reverse=True)[:10],
            "by_win_rate": sorted(active_players, key=lambda x: x["win_rate"], reverse=True)[:10],
            "by_average_score": sorted(active_players, key=lambda x: x["average_score"], reverse=True)[:10],
            "most_active": sorted(active_players, key=lambda x: x["tournaments_played"], reverse=True)[:10]
        }
