import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict
import math

class SerieAPredictionEngine:
    def __init__(self, data_fetcher, injury_scraper, transfer_scraper):
        self.data_fetcher = data_fetcher
        self.injury_scraper = injury_scraper
        self.transfer_scraper = transfer_scraper

        # Load and prepare historical data
        self.historical_data = self._load_historical_data()
        self.team_stats = self._calculate_team_statistics()

    def _load_historical_data(self):
        """Load multi-season historical data for training"""
        print("Loading historical data for predictions...")

        # Get data from multiple seasons
        seasons = ["2023-24", "2024-25"]  # Use recent complete seasons
        combined_data = self.data_fetcher.get_multiple_seasons_data(seasons)

        print(f"Loaded {len(combined_data)} historical matches")
        return combined_data

    def _calculate_team_statistics(self):
        """Calculate comprehensive team statistics for prediction"""
        team_stats = {}

        if self.historical_data.empty:
            return team_stats

        # Get unique teams
        home_teams = set(self.historical_data['HomeTeam'].unique())
        away_teams = set(self.historical_data['AwayTeam'].unique())
        all_teams = home_teams.union(away_teams)

        for team in all_teams:
            # Home matches
            home_matches = self.historical_data[self.historical_data['HomeTeam'] == team]
            # Away matches
            away_matches = self.historical_data[self.historical_data['AwayTeam'] == team]

            # Basic stats
            total_matches = len(home_matches) + len(away_matches)

            if total_matches == 0:
                continue

            # Results
            home_wins = len(home_matches[home_matches['FTR'] == 'H']) if 'FTR' in home_matches.columns else 0
            away_wins = len(away_matches[away_matches['FTR'] == 'A']) if 'FTR' in away_matches.columns else 0
            draws = (len(home_matches[home_matches['FTR'] == 'D']) +
                    len(away_matches[away_matches['FTR'] == 'D'])) if 'FTR' in self.historical_data.columns else 0

            # Goals
            goals_for_home = home_matches['FTHG'].sum() if 'FTHG' in home_matches.columns else 0
            goals_for_away = away_matches['FTAG'].sum() if 'FTAG' in away_matches.columns else 0
            goals_against_home = home_matches['FTAG'].sum() if 'FTAG' in home_matches.columns else 0
            goals_against_away = away_matches['FTHG'].sum() if 'FTHG' in away_matches.columns else 0

            total_goals_for = goals_for_home + goals_for_away
            total_goals_against = goals_against_home + goals_against_away

            # Advanced stats (if available)
            corners_for = 0
            corners_against = 0
            cards = 0

            if 'HC' in home_matches.columns:
                corners_for += home_matches['HC'].sum()
                corners_for += away_matches['AC'].sum() if 'AC' in away_matches.columns else 0
                corners_against += home_matches['AC'].sum() if 'AC' in home_matches.columns else 0
                corners_against += away_matches['HC'].sum() if 'HC' in away_matches.columns else 0

            if 'HY' in home_matches.columns:
                cards += home_matches['HY'].sum() + home_matches['HR'].sum() if 'HR' in home_matches.columns else 0
                cards += away_matches['AY'].sum() + away_matches['AR'].sum() if 'AR' in away_matches.columns else 0

            team_stats[team] = {
                'total_matches': total_matches,
                'wins': home_wins + away_wins,
                'draws': draws,
                'losses': total_matches - (home_wins + away_wins + draws),
                'goals_for': total_goals_for,
                'goals_against': total_goals_against,
                'goal_difference': total_goals_for - total_goals_against,
                'goals_per_match': total_goals_for / total_matches if total_matches > 0 else 0,
                'goals_conceded_per_match': total_goals_against / total_matches if total_matches > 0 else 0,
                'win_rate': (home_wins + away_wins) / total_matches if total_matches > 0 else 0,
                'home_win_rate': home_wins / len(home_matches) if len(home_matches) > 0 else 0,
                'away_win_rate': away_wins / len(away_matches) if len(away_matches) > 0 else 0,
                'corners_per_match': corners_for / total_matches if total_matches > 0 else 0,
                'cards_per_match': cards / total_matches if total_matches > 0 else 0
            }

        return team_stats

    def _get_recent_form(self, team, matches=5):
        """Get recent form for a team (last N matches)"""
        if self.historical_data.empty:
            return {'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0}

        # Get team's recent matches
        team_matches = self.historical_data[
            (self.historical_data['HomeTeam'] == team) |
            (self.historical_data['AwayTeam'] == team)
        ].copy()

        if team_matches.empty:
            return {'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0}

        # Sort by date (most recent first) - handle different date formats
        try:
            team_matches['Date'] = pd.to_datetime(team_matches['Date'])
            team_matches = team_matches.sort_values('Date', ascending=False)
        except:
            # If date parsing fails, just take the last N matches
            pass

        recent = team_matches.head(matches)

        wins = draws = losses = goals_for = goals_against = 0

        for _, match in recent.iterrows():
            if match['HomeTeam'] == team:
                # Team playing at home
                goals_for += match.get('FTHG', 0)
                goals_against += match.get('FTAG', 0)
                if match.get('FTR') == 'H':
                    wins += 1
                elif match.get('FTR') == 'D':
                    draws += 1
                else:
                    losses += 1
            else:
                # Team playing away
                goals_for += match.get('FTAG', 0)
                goals_against += match.get('FTHG', 0)
                if match.get('FTR') == 'A':
                    wins += 1
                elif match.get('FTR') == 'D':
                    draws += 1
                else:
                    losses += 1

        return {
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'form_points': wins * 3 + draws,  # Form in points
            'matches_analyzed': len(recent)
        }

    def _get_head_to_head(self, home_team, away_team, matches=5):
        """Get head-to-head record between two teams"""
        if self.historical_data.empty:
            return {'home_wins': 0, 'away_wins': 0, 'draws': 0, 'total_goals': 0}

        h2h_matches = self.historical_data[
            ((self.historical_data['HomeTeam'] == home_team) & (self.historical_data['AwayTeam'] == away_team)) |
            ((self.historical_data['HomeTeam'] == away_team) & (self.historical_data['AwayTeam'] == home_team))
        ]

        if h2h_matches.empty:
            return {'home_wins': 0, 'away_wins': 0, 'draws': 0, 'total_goals': 0, 'matches': 0}

        # Get recent H2H
        recent_h2h = h2h_matches.tail(matches)

        home_wins = away_wins = draws = total_goals = 0

        for _, match in recent_h2h.iterrows():
            total_goals += (match.get('FTHG', 0) + match.get('FTAG', 0))

            if match['HomeTeam'] == home_team:
                # Current home team was home in this historical match
                if match.get('FTR') == 'H':
                    home_wins += 1
                elif match.get('FTR') == 'A':
                    away_wins += 1
                else:
                    draws += 1
            else:
                # Current home team was away in this historical match
                if match.get('FTR') == 'A':
                    home_wins += 1
                elif match.get('FTR') == 'H':
                    away_wins += 1
                else:
                    draws += 1

        return {
            'home_wins': home_wins,
            'away_wins': away_wins,
            'draws': draws,
            'total_goals': total_goals,
            'avg_goals': total_goals / len(recent_h2h) if len(recent_h2h) > 0 else 0,
            'matches': len(recent_h2h)
        }

    def predict_match(self, home_team, away_team):
        """Generate comprehensive prediction for a match"""

        # Get team statistics
        home_stats = self.team_stats.get(home_team, {})
        away_stats = self.team_stats.get(away_team, {})

        # Get recent form
        home_form = self._get_recent_form(home_team)
        away_form = self._get_recent_form(away_team)

        # Get head-to-head
        h2h = self._get_head_to_head(home_team, away_team)

        # Get injury/transfer factors
        injury_impact = self._get_injury_impact(home_team, away_team)
        transfer_impact = self._get_transfer_impact(home_team, away_team)

        # Calculate predictions
        result_prediction = self._predict_result(home_stats, away_stats, home_form, away_form, h2h, injury_impact, transfer_impact)
        goals_prediction = self._predict_goals(home_stats, away_stats, home_form, away_form, h2h)
        advanced_prediction = self._predict_advanced_stats(home_stats, away_stats)

        prediction = {
            'match': f"{home_team} vs {away_team}",
            'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'result_prediction': result_prediction,
            'goals_prediction': goals_prediction,
            'advanced_prediction': advanced_prediction,
            'factors': {
                'home_form': home_form,
                'away_form': away_form,
                'head_to_head': h2h,
                'injury_impact': injury_impact,
                'transfer_impact': transfer_impact
            },
            'confidence': self._calculate_confidence(home_stats, away_stats, h2h)
        }

        return prediction

    def _get_injury_impact(self, home_team, away_team):
        """Get injury impact for both teams"""
        try:
            home_injuries = self.injury_scraper.get_team_injuries(home_team)
            away_injuries = self.injury_scraper.get_team_injuries(away_team)

            home_impact = sum(1 for inj in home_injuries if inj.get('status') == 'Out') * 0.1
            away_impact = sum(1 for inj in away_injuries if inj.get('status') == 'Out') * 0.1

            return {
                'home_impact': home_impact,
                'away_impact': away_impact,
                'home_injuries': len(home_injuries),
                'away_injuries': len(away_injuries)
            }
        except:
            return {'home_impact': 0, 'away_impact': 0, 'home_injuries': 0, 'away_injuries': 0}

    def _get_transfer_impact(self, home_team, away_team):
        """Get transfer impact for both teams"""
        try:
            strength_changes = self.transfer_scraper.get_team_strength_changes()

            home_impact = strength_changes.get(home_team, {}).get('net_impact', 0) * 0.01
            away_impact = strength_changes.get(away_team, {}).get('net_impact', 0) * 0.01

            return {
                'home_impact': home_impact,
                'away_impact': away_impact
            }
        except:
            return {'home_impact': 0, 'away_impact': 0}

    def _predict_result(self, home_stats, away_stats, home_form, away_form, h2h, injury_impact, transfer_impact):
        """Predict match result (1X2)"""

        # Base probabilities
        home_prob = 0.45  # Slight home advantage
        draw_prob = 0.25
        away_prob = 0.30

        # Adjust based on historical win rates
        if home_stats.get('home_win_rate', 0) > 0:
            home_prob += (home_stats['home_win_rate'] - 0.5) * 0.3
        if away_stats.get('away_win_rate', 0) > 0:
            away_prob += (away_stats['away_win_rate'] - 0.3) * 0.3

        # Adjust based on recent form (last 5 matches)
        home_form_factor = (home_form['wins'] - home_form['losses']) * 0.05
        away_form_factor = (away_form['wins'] - away_form['losses']) * 0.05

        home_prob += home_form_factor
        away_prob += away_form_factor

        # Adjust based on head-to-head
        if h2h['matches'] > 0:
            h2h_factor = 0.1
            if h2h['home_wins'] > h2h['away_wins']:
                home_prob += h2h_factor
            elif h2h['away_wins'] > h2h['home_wins']:
                away_prob += h2h_factor

        # Adjust for injuries and transfers
        home_prob += transfer_impact['home_impact'] - injury_impact['home_impact']
        away_prob += transfer_impact['away_impact'] - injury_impact['away_impact']

        # Normalize probabilities
        total = home_prob + draw_prob + away_prob
        if total > 0:
            home_prob /= total
            away_prob /= total
            draw_prob /= total

        # Ensure probabilities are within reasonable bounds
        home_prob = max(0.1, min(0.8, home_prob))
        away_prob = max(0.1, min(0.8, away_prob))
        draw_prob = max(0.1, min(0.5, draw_prob))

        # Final normalization
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        away_prob /= total
        draw_prob /= total

        # Determine most likely result
        if home_prob > away_prob and home_prob > draw_prob:
            prediction = "1"
            confidence = home_prob
        elif away_prob > home_prob and away_prob > draw_prob:
            prediction = "2"
            confidence = away_prob
        else:
            prediction = "X"
            confidence = draw_prob

        return {
            'prediction': prediction,
            'probabilities': {
                '1': round(home_prob * 100, 1),
                'X': round(draw_prob * 100, 1),
                '2': round(away_prob * 100, 1)
            },
            'confidence': round(confidence * 100, 1)
        }

    def _predict_goals(self, home_stats, away_stats, home_form, away_form, h2h):
        """Predict goals and over/under markets"""

        # Base goals prediction
        home_avg = home_stats.get('goals_per_match', 1.5)
        away_avg = away_stats.get('goals_per_match', 1.5)
        home_concede = home_stats.get('goals_conceded_per_match', 1.5)
        away_concede = away_stats.get('goals_conceded_per_match', 1.5)

        # Expected goals
        home_expected = (home_avg + away_concede) / 2
        away_expected = (away_avg + home_concede) / 2
        total_expected = home_expected + away_expected

        # Adjust based on recent form
        if home_form['matches_analyzed'] > 0:
            home_form_goals = home_form['goals_for'] / home_form['matches_analyzed']
            home_expected = (home_expected + home_form_goals) / 2

        if away_form['matches_analyzed'] > 0:
            away_form_goals = away_form['goals_for'] / away_form['matches_analyzed']
            away_expected = (away_expected + away_form_goals) / 2

        total_expected = home_expected + away_expected

        # Adjust based on H2H
        if h2h['matches'] > 0 and h2h['avg_goals'] > 0:
            total_expected = (total_expected + h2h['avg_goals']) / 2

        # Over/Under predictions
        over_2_5 = min(85, max(15, 50 + (total_expected - 2.5) * 20))
        over_1_5 = min(90, max(30, 60 + (total_expected - 1.5) * 25))

        return {
            'total_goals': round(total_expected, 1),
            'home_goals': round(home_expected, 1),
            'away_goals': round(away_expected, 1),
            'over_under': {
                'over_1_5': f"{over_1_5}%",
                'under_1_5': f"{100-over_1_5}%",
                'over_2_5': f"{over_2_5}%",
                'under_2_5': f"{100-over_2_5}%"
            },
            'both_teams_score': f"{min(75, max(25, 40 + (total_expected - 2) * 15))}%"
        }

    def _predict_advanced_stats(self, home_stats, away_stats):
        """Predict corners, cards, and other advanced statistics"""

        home_corners = home_stats.get('corners_per_match', 5.5)
        away_corners = away_stats.get('corners_per_match', 5.5)
        total_corners = home_corners + away_corners

        home_cards = home_stats.get('cards_per_match', 2.2)
        away_cards = away_stats.get('cards_per_match', 2.2)
        total_cards = home_cards + away_cards

        return {
            'corners': {
                'total': round(total_corners, 1),
                'home': round(home_corners, 1),
                'away': round(away_corners, 1),
                'over_9_5': f"{min(80, max(20, 50 + (total_corners - 9.5) * 10))}%",
                'over_10_5': f"{min(75, max(15, 45 + (total_corners - 10.5) * 10))}%"
            },
            'cards': {
                'total': round(total_cards, 1),
                'over_3_5': f"{min(70, max(30, 50 + (total_cards - 3.5) * 8))}%",
                'over_4_5': f"{min(60, max(20, 40 + (total_cards - 4.5) * 8))}%"
            }
        }

    def _calculate_confidence(self, home_stats, away_stats, h2h):
        """Calculate prediction confidence based on available data"""
        confidence = 60  # Base confidence

        # More data = higher confidence
        if home_stats.get('total_matches', 0) > 15:
            confidence += 10
        if away_stats.get('total_matches', 0) > 15:
            confidence += 10
        if h2h['matches'] > 3:
            confidence += 10

        # Clear favorite increases confidence
        home_strength = home_stats.get('win_rate', 0.5)
        away_strength = away_stats.get('win_rate', 0.5)

        if abs(home_strength - away_strength) > 0.2:
            confidence += 10

        return min(95, confidence)