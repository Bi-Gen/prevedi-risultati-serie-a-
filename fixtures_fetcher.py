import pandas as pd
import requests
import json
from datetime import datetime, timedelta

class SerieAFixturesFetcher:
    def __init__(self):
        self.current_season = "2025-26"
        self.fixture_sources = {
            "openfootball": f"https://raw.githubusercontent.com/openfootball/football.json/master/{self.current_season}/it.1.json"
        }

    def get_upcoming_fixtures(self, days_ahead=14):
        """Get upcoming Serie A fixtures in the next N days"""
        print(f"Fetching upcoming fixtures for next {days_ahead} days...")

        try:
            # Get current season fixtures
            response = requests.get(self.fixture_sources["openfootball"], timeout=10)
            data = response.json()

            upcoming_matches = []
            today = datetime.now()
            cutoff_date = today + timedelta(days=days_ahead)

            if 'matches' in data:
                for match in data['matches']:
                    match_date_str = match.get('date', '')

                    try:
                        # Parse various date formats
                        if match_date_str:
                            # Try different date formats
                            for date_format in ['%Y-%m-%d', '%Y/%m/%d', '%d.%m.%Y', '%d/%m/%Y']:
                                try:
                                    match_date = datetime.strptime(match_date_str, date_format)
                                    break
                                except ValueError:
                                    continue
                            else:
                                # If no format works, skip this match
                                continue

                            # Check if match is upcoming
                            if today <= match_date <= cutoff_date:
                                # Check if match hasn't been played (no score)
                                if match.get('score1') is None or match.get('score2') is None:
                                    upcoming_matches.append({
                                        'date': match_date.strftime('%Y-%m-%d'),
                                        'home_team': match.get('team1', ''),
                                        'away_team': match.get('team2', ''),
                                        'round': match.get('round', ''),
                                        'time': match.get('time', ''),
                                        'matchday': match.get('matchday', ''),
                                        'days_from_now': (match_date - today).days
                                    })
                    except Exception as e:
                        print(f"Error parsing match date {match_date_str}: {e}")
                        continue

            # Sort by date
            upcoming_matches = sorted(upcoming_matches, key=lambda x: x['date'])

            print(f"Found {len(upcoming_matches)} upcoming matches")
            return upcoming_matches

        except Exception as e:
            print(f"Error fetching fixtures: {e}")
            return self._get_dummy_fixtures()

    def _get_dummy_fixtures(self):
        """Generate dummy upcoming fixtures for demonstration"""
        print("Creating dummy upcoming fixtures...")

        today = datetime.now()

        dummy_fixtures = [
            {
                'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                'home_team': 'Inter',
                'away_team': 'Juventus',
                'round': 'Matchday 10',
                'time': '20:45',
                'matchday': 10,
                'days_from_now': 2
            },
            {
                'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'home_team': 'Milan',
                'away_team': 'Napoli',
                'round': 'Matchday 10',
                'time': '18:00',
                'matchday': 10,
                'days_from_now': 3
            },
            {
                'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'home_team': 'Roma',
                'away_team': 'Lazio',
                'round': 'Matchday 10',
                'time': '20:45',
                'matchday': 10,
                'days_from_now': 3
            },
            {
                'date': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
                'home_team': 'Atalanta',
                'away_team': 'Fiorentina',
                'round': 'Matchday 10',
                'time': '15:00',
                'matchday': 10,
                'days_from_now': 4
            },
            {
                'date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
                'home_team': 'Bologna',
                'away_team': 'Torino',
                'round': 'Matchday 11',
                'time': '18:30',
                'matchday': 11,
                'days_from_now': 7
            },
            {
                'date': (today + timedelta(days=8)).strftime('%Y-%m-%d'),
                'home_team': 'Genoa',
                'away_team': 'Udinese',
                'round': 'Matchday 11',
                'time': '15:00',
                'matchday': 11,
                'days_from_now': 8
            }
        ]

        return dummy_fixtures

    def get_next_round_fixtures(self):
        """Get all fixtures for the next matchday"""
        upcoming = self.get_upcoming_fixtures(days_ahead=10)

        if not upcoming:
            return []

        # Find the next matchday
        next_matchday = min(match['matchday'] for match in upcoming if isinstance(match['matchday'], int))

        # Get all matches for this matchday
        next_round = [match for match in upcoming if match['matchday'] == next_matchday]

        return next_round

    def get_big_matches(self, days_ahead=30):
        """Get upcoming big matches (Derby, Top teams)"""
        big_teams = ['Inter', 'Juventus', 'Milan', 'Napoli', 'Roma', 'Lazio', 'Atalanta', 'Fiorentina']

        upcoming = self.get_upcoming_fixtures(days_ahead)

        big_matches = []
        for match in upcoming:
            home = match['home_team']
            away = match['away_team']

            # Derby matches
            if (home in ['Inter', 'Milan'] and away in ['Inter', 'Milan']) or \
               (home in ['Roma', 'Lazio'] and away in ['Roma', 'Lazio']) or \
               (home in ['Juventus', 'Torino'] and away in ['Juventus', 'Torino']):
                match['match_type'] = 'Derby'
                big_matches.append(match)
            # Top team clashes
            elif home in big_teams and away in big_teams:
                match['match_type'] = 'Big Match'
                big_matches.append(match)

        return big_matches

    def get_fixtures_by_team(self, team_name, days_ahead=30):
        """Get upcoming fixtures for a specific team"""
        upcoming = self.get_upcoming_fixtures(days_ahead)

        team_fixtures = [
            match for match in upcoming
            if match['home_team'].lower() == team_name.lower() or
               match['away_team'].lower() == team_name.lower()
        ]

        # Add venue information
        for fixture in team_fixtures:
            if fixture['home_team'].lower() == team_name.lower():
                fixture['venue'] = 'Home'
                fixture['opponent'] = fixture['away_team']
            else:
                fixture['venue'] = 'Away'
                fixture['opponent'] = fixture['home_team']

        return team_fixtures

if __name__ == "__main__":
    fetcher = SerieAFixturesFetcher()

    print("=== Testing Fixtures Fetcher ===")

    # Test upcoming fixtures
    upcoming = fetcher.get_upcoming_fixtures(7)
    print(f"\nUpcoming fixtures (next 7 days): {len(upcoming)}")
    for fixture in upcoming[:3]:
        print(f"  {fixture['date']}: {fixture['home_team']} vs {fixture['away_team']} ({fixture['days_from_now']} days)")

    # Test next round
    next_round = fetcher.get_next_round_fixtures()
    print(f"\nNext matchday: {len(next_round)} matches")

    # Test big matches
    big_matches = fetcher.get_big_matches(14)
    print(f"\nBig matches (next 14 days): {len(big_matches)}")
    for match in big_matches:
        print(f"  {match['date']}: {match['home_team']} vs {match['away_team']} ({match['match_type']})")

    # Test team fixtures
    inter_fixtures = fetcher.get_fixtures_by_team('Inter', 14)
    print(f"\nInter fixtures (next 14 days): {len(inter_fixtures)}")
    for fixture in inter_fixtures:
        print(f"  {fixture['date']}: vs {fixture['opponent']} ({fixture['venue']})")