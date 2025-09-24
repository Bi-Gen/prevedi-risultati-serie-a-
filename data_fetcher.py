import pandas as pd
import requests
from datetime import datetime

class SerieADataFetcher:
    def __init__(self):
        # DataHub Serie A dataset URL
        self.base_url = "https://datahub.io/sports-data/italian-serie-a/r/"

    def fetch_season_data(self, season="2023-24"):
        """Fetch Serie A data for specific season"""
        try:
            # URL per i dati Serie A da DataHub
            url = f"{self.base_url}italian-serie-a-{season}.csv"
            print(f"Fetching data from: {url}")

            df = pd.read_csv(url)
            print(f"Successfully loaded {len(df)} matches")
            return df

        except Exception as e:
            print(f"Error fetching data: {e}")
            # Fallback: crea dati dummy per test
            return self.create_dummy_data()

    def create_dummy_data(self):
        """Create dummy data for testing"""
        print("Creating dummy test data...")
        dummy_data = {
            'Date': ['2024-01-20', '2024-01-21', '2024-01-22'],
            'HomeTeam': ['Juventus', 'Inter', 'Milan'],
            'AwayTeam': ['Roma', 'Napoli', 'Lazio'],
            'FTHG': [2, 1, 0],  # Full Time Home Goals
            'FTAG': [1, 1, 2],  # Full Time Away Goals
            'FTR': ['H', 'D', 'A']  # Full Time Result
        }
        return pd.DataFrame(dummy_data)

    def get_basic_stats(self, df):
        """Get basic statistics from the data"""
        stats = {
            'total_matches': len(df),
            'home_wins': len(df[df['FTR'] == 'H']) if 'FTR' in df.columns else 0,
            'away_wins': len(df[df['FTR'] == 'A']) if 'FTR' in df.columns else 0,
            'draws': len(df[df['FTR'] == 'D']) if 'FTR' in df.columns else 0
        }
        return stats

    def get_teams(self, df):
        """Extract unique teams from match data"""
        teams = []
        if 'HomeTeam' in df.columns and 'AwayTeam' in df.columns:
            home_teams = set(df['HomeTeam'].unique())
            away_teams = set(df['AwayTeam'].unique())
            all_teams = home_teams.union(away_teams)

            for team in sorted(all_teams):
                # Get team stats
                home_matches = df[df['HomeTeam'] == team]
                away_matches = df[df['AwayTeam'] == team]

                total_matches = len(home_matches) + len(away_matches)

                if 'FTR' in df.columns:
                    home_wins = len(home_matches[home_matches['FTR'] == 'H'])
                    away_wins = len(away_matches[away_matches['FTR'] == 'A'])
                    total_wins = home_wins + away_wins

                    home_draws = len(home_matches[home_matches['FTR'] == 'D'])
                    away_draws = len(away_matches[away_matches['FTR'] == 'D'])
                    total_draws = home_draws + away_draws

                    total_losses = total_matches - total_wins - total_draws
                else:
                    total_wins = total_draws = total_losses = 0

                teams.append({
                    'name': team,
                    'matches_played': total_matches,
                    'wins': total_wins,
                    'draws': total_draws,
                    'losses': total_losses
                })

        return teams

if __name__ == "__main__":
    fetcher = SerieADataFetcher()
    data = fetcher.fetch_season_data()
    print("\nData sample:")
    print(data.head())

    stats = fetcher.get_basic_stats(data)
    print(f"\nBasic stats: {stats}")