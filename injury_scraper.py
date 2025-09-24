import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

class InjuryDataScraper:
    def __init__(self):
        self.base_urls = {
            "sportsgambler": "https://www.sportsgambler.com/injuries/football/italy-serie-a/",
            "transfermarkt": "https://www.transfermarkt.com/serie-a/verletztenspieler/wettbewerb/IT1"
        }

        # Serie A team mapping for consistent naming
        self.team_mapping = {
            'AC Milan': 'Milan',
            'Inter Milan': 'Inter',
            'AS Roma': 'Roma',
            'Hellas Verona': 'Verona',
            'Juventus FC': 'Juventus',
            'SSC Napoli': 'Napoli',
            'ACF Fiorentina': 'Fiorentina',
            'Atalanta BC': 'Atalanta',
            'Bologna FC': 'Bologna',
            'Cagliari Calcio': 'Cagliari',
            'Como 1907': 'Como',
            'Empoli FC': 'Empoli',
            'Genoa CFC': 'Genoa',
            'US Lecce': 'Lecce',
            'SS Lazio': 'Lazio',
            'Monza': 'Monza',
            'Parma Calcio': 'Parma',
            'Torino FC': 'Torino',
            'Udinese Calcio': 'Udinese',
            'Venezia FC': 'Venezia'
        }

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_dummy_injury_data(self):
        """Generate realistic dummy injury data for Serie A teams"""
        print("Creating dummy injury data for Serie A teams...")

        dummy_injuries = [
            {
                'team': 'Inter',
                'player': 'Lautaro Martinez',
                'position': 'Forward',
                'injury': 'Hamstring Strain',
                'status': 'Out',
                'expected_return': '2025-10-15',
                'days_out': 12
            },
            {
                'team': 'Milan',
                'player': 'Rafael Leao',
                'position': 'Forward',
                'injury': 'Ankle Injury',
                'status': 'Doubtful',
                'expected_return': '2025-10-05',
                'days_out': 3
            },
            {
                'team': 'Juventus',
                'player': 'Paul Pogba',
                'position': 'Midfielder',
                'injury': 'Knee Surgery',
                'status': 'Out',
                'expected_return': '2025-11-20',
                'days_out': 45
            },
            {
                'team': 'Napoli',
                'player': 'Victor Osimhen',
                'position': 'Forward',
                'injury': 'Muscle Fatigue',
                'status': 'Questionable',
                'expected_return': '2025-10-06',
                'days_out': 2
            },
            {
                'team': 'Roma',
                'player': 'Lorenzo Pellegrini',
                'position': 'Midfielder',
                'injury': 'Calf Strain',
                'status': 'Out',
                'expected_return': '2025-10-10',
                'days_out': 8
            },
            {
                'team': 'Atalanta',
                'player': 'Duvan Zapata',
                'position': 'Forward',
                'injury': 'Thigh Injury',
                'status': 'Out',
                'expected_return': '2025-10-20',
                'days_out': 18
            },
            {
                'team': 'Fiorentina',
                'player': 'Nico Gonzalez',
                'position': 'Forward',
                'injury': 'Groin Strain',
                'status': 'Doubtful',
                'expected_return': '2025-10-07',
                'days_out': 4
            },
            {
                'team': 'Lazio',
                'player': 'Ciro Immobile',
                'position': 'Forward',
                'injury': 'Back Pain',
                'status': 'Questionable',
                'expected_return': '2025-10-05',
                'days_out': 1
            }
        ]

        return pd.DataFrame(dummy_injuries)

    def scrape_injury_data(self):
        """Scrape injury data from multiple sources"""
        print("Attempting to scrape injury data...")

        # For now, return dummy data as scraping requires handling anti-bot measures
        # In production, you'd implement proper scraping with delays, proxies, etc.
        try:
            # Placeholder for actual scraping logic
            response = requests.get(self.base_urls["sportsgambler"], headers=self.headers, timeout=10)

            if response.status_code != 200:
                print(f"Scraping failed (status {response.status_code}), using dummy data")
                return self.get_dummy_injury_data()

            # Would implement BeautifulSoup parsing here
            print("Scraping successful but parsing not implemented, using dummy data")
            return self.get_dummy_injury_data()

        except Exception as e:
            print(f"Scraping error: {e}, using dummy data")
            return self.get_dummy_injury_data()

    def get_team_injuries(self, team_name):
        """Get injuries for specific team"""
        all_injuries = self.scrape_injury_data()
        team_injuries = all_injuries[all_injuries['team'].str.lower() == team_name.lower()]
        return team_injuries.to_dict('records')

    def get_injury_summary(self):
        """Get summary of all injuries across Serie A"""
        all_injuries = self.scrape_injury_data()

        summary = {
            'total_injuries': len(all_injuries),
            'by_status': all_injuries['status'].value_counts().to_dict(),
            'by_team': all_injuries['team'].value_counts().to_dict(),
            'by_position': all_injuries['position'].value_counts().to_dict(),
            'most_common_injuries': all_injuries['injury'].value_counts().head(5).to_dict(),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return summary

    def get_availability_impact(self):
        """Calculate impact of injuries on team availability"""
        all_injuries = self.scrape_injury_data()

        impact = []
        for team in all_injuries['team'].unique():
            team_injuries = all_injuries[all_injuries['team'] == team]

            out_players = len(team_injuries[team_injuries['status'] == 'Out'])
            doubtful_players = len(team_injuries[team_injuries['status'] == 'Doubtful'])

            impact_score = out_players * 1.0 + doubtful_players * 0.5

            impact.append({
                'team': team,
                'total_injuries': len(team_injuries),
                'players_out': out_players,
                'players_doubtful': doubtful_players,
                'impact_score': impact_score,
                'key_players_out': team_injuries[team_injuries['position'].isin(['Forward', 'Midfielder'])]['player'].tolist()
            })

        # Sort by impact score
        impact = sorted(impact, key=lambda x: x['impact_score'], reverse=True)

        return impact

if __name__ == "__main__":
    scraper = InjuryDataScraper()

    print("=== Testing Injury Data Scraper ===")

    # Test injury summary
    summary = scraper.get_injury_summary()
    print(f"\nInjury Summary:")
    print(f"Total injuries: {summary['total_injuries']}")
    print(f"By status: {summary['by_status']}")

    # Test team-specific injuries
    inter_injuries = scraper.get_team_injuries('Inter')
    print(f"\nInter injuries: {len(inter_injuries)} players")
    for injury in inter_injuries:
        print(f"  - {injury['player']} ({injury['position']}): {injury['injury']} - {injury['status']}")

    # Test availability impact
    impact = scraper.get_availability_impact()
    print(f"\nTeams most affected by injuries:")
    for team_impact in impact[:5]:
        print(f"  {team_impact['team']}: {team_impact['impact_score']} impact score ({team_impact['players_out']} out, {team_impact['players_doubtful']} doubtful)")