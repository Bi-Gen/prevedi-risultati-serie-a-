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

if __name__ == "__main__":
    fetcher = SerieADataFetcher()
    data = fetcher.fetch_season_data()
    print("\nData sample:")
    print(data.head())

    stats = fetcher.get_basic_stats(data)
    print(f"\nBasic stats: {stats}")