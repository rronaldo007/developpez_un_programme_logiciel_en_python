import random
from typing import List, Tuple, Dict
from collections import defaultdict
from models.player import Player


class TournamentPairingHelper:

    @staticmethod
    def generate_pairs_for_next_round(tournament) -> List[Tuple]:
        if len(tournament.players) % 2 != 0:
            raise ValueError("Nombre impair de joueurs")

        if tournament.current_round == 0:
            return TournamentPairingHelper._generate_first_round_pairs(
                tournament.players
            )
        else:
            return TournamentPairingHelper._generate_swiss_pairs(tournament)

    @staticmethod
    def _generate_first_round_pairs(players: List) -> List[Tuple]:
        players_copy = players.copy()
        random.shuffle(players_copy)

        pairs = []
        for i in range(0, len(players_copy), 2):
            pairs.append((players_copy[i], players_copy[i + 1]))

        return pairs

    @staticmethod
    def _generate_swiss_pairs(tournament) -> List[Tuple]:
        sorted_players = sorted(
            tournament.players,
            key=lambda p: (
                -tournament.get_player_score(p.national_id),
                p.last_name,
                p.first_name
            )
        )

        pairs = []
        available_players = sorted_players.copy()

        while len(available_players) >= 2:
            player1 = available_players.pop(0)

            opponent_found = False
            for i, player2 in enumerate(available_players):
                if not TournamentPairingHelper._have_played_against(
                    tournament, player1, player2
                ):
                    pairs.append((player1, player2))
                    available_players.pop(i)
                    opponent_found = True
                    break

            if not opponent_found and available_players:
                player2 = available_players.pop(0)
                pairs.append((player1, player2))

        return pairs

    @staticmethod
    def _have_played_against(tournament, player1: Player,
                             player2: Player) -> bool:
        for round_obj in tournament.rounds:
            for match in round_obj.matches:
                if ((match.player1_national_id == player1.national_id and
                     match.player2_national_id == player2.national_id) or
                    (match.player1_national_id == player2.national_id and
                     match.player2_national_id == player1.national_id)):
                    return True
        return False


class TournamentValidationHelper:

    @staticmethod
    def validate_tournament_state(tournament) -> List[str]:
        errors = []

        errors.extend(
            TournamentValidationHelper._validate_players(tournament)
        )

        errors.extend(
            TournamentValidationHelper._validate_rounds(tournament)
        )

        errors.extend(
            TournamentValidationHelper._validate_consistency(tournament)
        )

        return errors

    @staticmethod
    def _validate_players(tournament) -> List[str]:
        """Valide les joueurs du tournoi"""
        errors = []

        if len(tournament.players) < 2:
            errors.append("Au moins 2 joueurs requis")

        if len(tournament.players) % 2 != 0:
            errors.append("Le nombre de joueurs doit être pair")

        seen_ids = set()
        for player in tournament.players:
            if player.national_id in seen_ids:
                errors.append(f"ID joueur dupliqué: {player.national_id}")
            seen_ids.add(player.national_id)

        return errors

    @staticmethod
    def _validate_rounds(tournament) -> List[str]:
        errors = []

        for i, round_obj in enumerate(tournament.rounds):
            round_number = i + 1

            if not round_obj.matches:
                errors.append(f"Tour {round_number}: Aucun match")
                continue

            players_in_round = []
            for match in round_obj.matches:
                players_in_round.extend([
                    match.player1_national_id, match.player2_national_id
                ])

            seen_in_round = set()
            for player_id in players_in_round:
                if player_id in seen_in_round:
                    errors.append(
                        f"Tour {round_number}: Joueur {player_id} "
                        "joue plusieurs fois"
                    )
                seen_in_round.add(player_id)

            tournament_player_ids = {p.national_id for p in tournament.players}
            round_player_ids = set(players_in_round)

            missing_players = tournament_player_ids - round_player_ids
            if missing_players:
                errors.append(
                    f"Tour {round_number}: Joueurs manquants: "
                    f"{', '.join(missing_players)}"
                )

            extra_players = round_player_ids - tournament_player_ids
            if extra_players:
                errors.append(
                    f"Tour {round_number}: Joueurs non inscrits: "
                    f"{', '.join(extra_players)}"
                )

        return errors

    @staticmethod
    def _validate_consistency(tournament) -> List[str]:
        errors = []

        if tournament.current_round != len(tournament.rounds):
            errors.append(
                f"Incohérence: current_round={tournament.current_round}, "
                f"tours réels={len(tournament.rounds)}"
            )

        for i, round_obj in enumerate(tournament.rounds):
            if round_obj.is_finished and not round_obj.all_matches_finished():
                errors.append(
                    f"Tour {i+1}: Marqué terminé mais des matchs "
                    "sont incomplets"
                )

        if tournament.rounds:
            last_round = tournament.rounds[-1]
            if not last_round.is_finished and tournament.is_finished():
                errors.append(
                    "Tournoi marqué terminé mais le dernier tour "
                    "n'est pas fini"
                )

        return errors


class TournamentStatisticsHelper:

    @staticmethod
    def calculate_tournament_statistics(tournament) -> Dict:
        stats = {
            'basic_info': TournamentStatisticsHelper._get_basic_info(
                tournament
            ),
            'participation': TournamentStatisticsHelper._get_participation_stats(
                tournament
            ),
            'match_results': TournamentStatisticsHelper._get_match_results(
                tournament
            ),
            'performance': TournamentStatisticsHelper._get_performance_stats(
                tournament
            ),
            'progression': TournamentStatisticsHelper._get_progression_stats(
                tournament
            )
        }

        return stats

    @staticmethod
    def _get_basic_info(tournament) -> Dict:
        total_matches = sum(
            len(round_obj.matches) for round_obj in tournament.rounds
        )
        finished_matches = sum(
            len(round_obj.get_finished_matches())
            for round_obj in tournament.rounds
        )

        completion_rate = 0
        if total_matches > 0:
            completion_rate = (finished_matches / total_matches * 100)

        status = 'Non commencé'
        if tournament.is_finished():
            status = 'Terminé'
        elif tournament.has_started():
            status = 'En cours'

        return {
            'name': tournament.name,
            'location': tournament.location,
            'players_count': len(tournament.players),
            'rounds_planned': tournament.number_of_rounds,
            'rounds_played': len(tournament.rounds),
            'total_matches': total_matches,
            'finished_matches': finished_matches,
            'completion_rate': completion_rate,
            'is_finished': tournament.is_finished(),
            'status': status
        }

    @staticmethod
    def _get_participation_stats(tournament) -> Dict:
        if not tournament.rounds:
            return {'active_players': 0, 'participation_rate': 0}

        active_players = set()
        for round_obj in tournament.rounds:
            for match in round_obj.matches:
                active_players.add(match.player1_national_id)
                active_players.add(match.player2_national_id)

        participation_rate = 0
        if tournament.players:
            participation_rate = (
                len(active_players) / len(tournament.players) * 100
            )

        return {
            'registered_players': len(tournament.players),
            'active_players': len(active_players),
            'participation_rate': participation_rate
        }

    @staticmethod
    def _get_match_results(tournament) -> Dict:
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

        draw_rate = 0
        decisive_rate = 0
        if total_finished > 0:
            draw_rate = (draws / total_finished * 100)
            decisive_rate = (wins / total_finished * 100)

        return {
            'total_finished_matches': total_finished,
            'decisive_games': wins,
            'draws': draws,
            'draw_rate': draw_rate,
            'decisive_rate': decisive_rate
        }

    @staticmethod
    def _get_performance_stats(tournament) -> Dict:
        if not tournament.players:
            return {}

        scores = [
            tournament.get_player_score(p.national_id)
            for p in tournament.players
        ]
        scores.sort(reverse=True)

        total_score = sum(scores)
        avg_score = total_score / len(scores)

        max_score = max(scores) if scores else 0
        leaders = [
            p for p in tournament.players
            if tournament.get_player_score(p.national_id) == max_score
        ]

        score_distribution = defaultdict(int)
        for score in scores:
            score_distribution[score] += 1

        score_spread = 0
        if scores:
            score_spread = max_score - min(scores)

        return {
            'average_score': avg_score,
            'highest_score': max_score,
            'lowest_score': min(scores) if scores else 0,
            'leaders_count': len(leaders),
            'score_spread': score_spread,
            'score_distribution': dict(score_distribution)
        }

    @staticmethod
    def _get_progression_stats(tournament) -> Dict:
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

            finished_matches = round_obj.get_finished_matches()
            wins = sum(1 for match in finished_matches if not match.is_draw())
            draws = sum(1 for match in finished_matches if match.is_draw())

            draw_rate = 0
            if finished_matches:
                draw_rate = (draws / len(finished_matches) * 100)

            round_stats.update({
                'wins': wins,
                'draws': draws,
                'draw_rate': draw_rate
            })

            rounds_data.append(round_stats)

        return {'rounds_data': rounds_data}
