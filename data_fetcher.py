import pandas as pd
import requests
from datetime import datetime

class SerieADataFetcher:
    def __init__(self):
        # Multiple data sources for different seasons
        self.data_sources = {
            "datahub": "https://r2.datahub.io/cm2t6nt7l0000ma0cqp9qgewa/main/raw/",
            "openfootball_csv": "https://raw.githubusercontent.com/footballcsv/cache.footballdata/master/",
            "openfootball_json": "https://raw.githubusercontent.com/openfootball/football.json/master/"
        }

    def fetch_season_data(self, season="2024-25"):
        """Fetch Serie A data for specific season with multiple sources"""
        print(f"Fetching Serie A data for season {season}...")

        # Try different sources based on season
        if season == "2024-25":
            return self._fetch_datahub_season(season)
        elif season == "2025-26":
            return self._fetch_current_season(season)
        else:
            # Fallback to old Football-CSV for historical data
            return self._fetch_footballcsv_season(season)

    def _fetch_datahub_season(self, season):
        """Fetch from DataHub (best for 2024-25 complete season)"""
        try:
            # DataHub format: season-2425.csv
            season_code = season.replace("-", "").replace("20", "")  # "2024-25" -> "2425"
            url = f"{self.data_sources['datahub']}season-{season_code}.csv"
            print(f"Fetching from DataHub: {url}")

            df = pd.read_csv(url)
            print(f"Successfully loaded {len(df)} matches from DataHub")
            return self._standardize_datahub_format(df)

        except Exception as e:
            print(f"DataHub failed: {e}")
            return self._fetch_footballcsv_season(season)

    def _fetch_current_season(self, season):
        """Fetch current 2025-26 season from OpenFootball JSON"""
        try:
            # OpenFootball JSON format for current season
            url = f"{self.data_sources['openfootball_json']}{season}/it.1.json"
            print(f"Fetching current season from OpenFootball: {url}")

            import requests
            response = requests.get(url)
            json_data = response.json()

            # Convert JSON to DataFrame
            matches = []
            if 'matches' in json_data:
                for match in json_data['matches']:
                    matches.append({
                        'Date': match.get('date', ''),
                        'HomeTeam': match.get('team1', ''),
                        'AwayTeam': match.get('team2', ''),
                        'FTHG': match.get('score1', 0) if match.get('score1') is not None else None,
                        'FTAG': match.get('score2', 0) if match.get('score2') is not None else None,
                        'FTR': self._calculate_result(match.get('score1'), match.get('score2'))
                    })

            df = pd.DataFrame(matches)
            print(f"Successfully loaded {len(df)} matches from OpenFootball")
            return df

        except Exception as e:
            print(f"OpenFootball current season failed: {e}")
            return self._fetch_footballcsv_season(season)

    def _fetch_footballcsv_season(self, season):
        """Fallback to Football-CSV (for historical data)"""
        try:
            url = f"{self.data_sources['openfootball_csv']}{season}/it.1.csv"
            print(f"Fetching from Football-CSV: {url}")

            df = pd.read_csv(url)
            df = self.standardize_data(df)  # Use existing method

            print(f"Successfully loaded {len(df)} matches from Football-CSV")
            return df

        except Exception as e:
            print(f"All sources failed: {e}")
            return self.create_dummy_data()

    def _standardize_datahub_format(self, df):
        """Standardize DataHub CSV format"""
        # DataHub already has standard format: Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, etc.
        if all(col in df.columns for col in ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']):
            # Calculate FTR if missing
            if 'FTR' not in df.columns:
                df['FTR'] = df.apply(
                    lambda row: 'H' if row['FTHG'] > row['FTAG']
                               else 'A' if row['FTHG'] < row['FTAG']
                               else 'D', axis=1
                )
            return df
        else:
            # If format is different, use existing standardization
            return self.standardize_data(df)

    def _calculate_result(self, score1, score2):
        """Calculate match result from scores"""
        if score1 is None or score2 is None:
            return None  # Match not played yet
        return 'H' if score1 > score2 else 'A' if score1 < score2 else 'D'

    def get_multiple_seasons_data(self, seasons=["2023-24", "2024-25", "2025-26"]):
        """Get data from multiple seasons for better predictions"""
        all_data = []

        for season in seasons:
            print(f"\n=== Fetching season {season} ===")
            season_data = self.fetch_season_data(season)
            if not season_data.empty:
                season_data['Season'] = season
                all_data.append(season_data)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"\n=== Total: {len(combined_df)} matches across {len(seasons)} seasons ===")
            return combined_df
        else:
            return self.create_dummy_data()

    def standardize_data(self, df):
        """Convert Football-CSV format to standard format"""
        # Football-CSV format: Date, Team 1, FT, HT, Team 2
        standardized_df = pd.DataFrame()

        if 'Team 1' in df.columns and 'Team 2' in df.columns:
            standardized_df['Date'] = df['Date']
            standardized_df['HomeTeam'] = df['Team 1']
            standardized_df['AwayTeam'] = df['Team 2']

            # Parse FT scores (e.g., "2-1" -> FTHG=2, FTAG=1)
            if 'FT' in df.columns:
                ft_scores = df['FT'].str.split('-', expand=True)
                standardized_df['FTHG'] = pd.to_numeric(ft_scores[0], errors='coerce')
                standardized_df['FTAG'] = pd.to_numeric(ft_scores[1], errors='coerce')

                # Calculate result (H/A/D)
                standardized_df['FTR'] = standardized_df.apply(
                    lambda row: 'H' if row['FTHG'] > row['FTAG']
                               else 'A' if row['FTHG'] < row['FTAG']
                               else 'D', axis=1
                )

            # Parse HT scores if available
            if 'HT' in df.columns:
                ht_scores = df['HT'].str.split('-', expand=True)
                standardized_df['HTHG'] = pd.to_numeric(ht_scores[0], errors='coerce')
                standardized_df['HTAG'] = pd.to_numeric(ht_scores[1], errors='coerce')

        return standardized_df

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