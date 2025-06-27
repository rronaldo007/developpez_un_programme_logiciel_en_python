from typing import Dict


class MatchAnalysisHelper:

    @staticmethod
    def analyze_match_result(match) -> Dict:
        if not match.is_finished:
            return {
                'status': 'unfinished',
                'players': [
                    match.player1_national_id, match.player2_national_id
                ],
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
        if match.is_draw():
            return "Match nul"

        winner_id = match.get_winner_id()

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
