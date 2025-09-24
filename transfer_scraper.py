import requests
import pandas as pd
import json
from datetime import datetime, timedelta

class TransferDataScraper:
    def __init__(self):
        self.base_urls = {
            "transfermarkt": "https://www.transfermarkt.com/transfers/transfertageaktuell/statistik",
            "football_italia": "https://football-italia.net/category/transfers/",
            "sky_sports": "https://www.skysports.com/transfer-centre"
        }

        # Serie A teams for filtering transfers
        self.serie_a_teams = [
            'Inter', 'Milan', 'Juventus', 'Roma', 'Napoli', 'Atalanta',
            'Lazio', 'Fiorentina', 'Bologna', 'Torino', 'Verona',
            'Udinese', 'Cagliari', 'Genoa', 'Lecce', 'Empoli',
            'Monza', 'Parma', 'Como', 'Venezia'
        ]

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_dummy_transfer_data(self):
        """Generate realistic dummy transfer data for Serie A teams"""
        print("Creating dummy transfer data for Serie A...")

        # Recent transfer window activity (dummy data)
        dummy_transfers = [
            {
                'player': 'Romelu Lukaku',
                'from_team': 'Chelsea',
                'to_team': 'Napoli',
                'transfer_type': 'Loan',
                'fee': '€0 (Loan)',
                'date': '2024-08-30',
                'position': 'Forward',
                'age': 31,
                'contract_length': '1 year loan',
                'market_value': '€25M',
                'impact_rating': 9.0
            },
            {
                'player': 'Teun Koopmeiners',
                'from_team': 'Atalanta',
                'to_team': 'Juventus',
                'transfer_type': 'Permanent',
                'fee': '€51M',
                'date': '2024-08-28',
                'position': 'Midfielder',
                'age': 26,
                'contract_length': '5 years',
                'market_value': '€55M',
                'impact_rating': 8.5
            },
            {
                'player': 'Alvaro Morata',
                'from_team': 'Atletico Madrid',
                'to_team': 'Milan',
                'transfer_type': 'Permanent',
                'fee': '€13M',
                'date': '2024-08-15',
                'position': 'Forward',
                'age': 31,
                'contract_length': '4 years',
                'market_value': '€18M',
                'impact_rating': 7.5
            },
            {
                'player': 'Piotr Zielinski',
                'from_team': 'Napoli',
                'to_team': 'Inter',
                'transfer_type': 'Free Transfer',
                'fee': '€0',
                'date': '2024-08-10',
                'position': 'Midfielder',
                'age': 30,
                'contract_length': '3 years',
                'market_value': '€20M',
                'impact_rating': 7.0
            },
            {
                'player': 'Mateo Retegui',
                'from_team': 'Genoa',
                'to_team': 'Atalanta',
                'transfer_type': 'Permanent',
                'fee': '€22M',
                'date': '2024-08-12',
                'position': 'Forward',
                'age': 25,
                'contract_length': '5 years',
                'market_value': '€25M',
                'impact_rating': 6.5
            },
            {
                'player': 'Albert Gudmundsson',
                'from_team': 'Genoa',
                'to_team': 'Fiorentina',
                'transfer_type': 'Loan with option',
                'fee': '€8M loan + €17M option',
                'date': '2024-08-25',
                'position': 'Forward',
                'age': 27,
                'contract_length': '1+4 years',
                'market_value': '€30M',
                'impact_rating': 7.8
            },
            {
                'player': 'Douglas Luiz',
                'from_team': 'Aston Villa',
                'to_team': 'Juventus',
                'transfer_type': 'Permanent',
                'fee': '€50M',
                'date': '2024-08-05',
                'position': 'Midfielder',
                'age': 26,
                'contract_length': '5 years',
                'market_value': '€45M',
                'impact_rating': 8.0
            },
            {
                'player': 'Valentín Carboni',
                'from_team': 'Inter',
                'to_team': 'Monza',
                'transfer_type': 'Loan',
                'fee': '€0 (Loan)',
                'date': '2024-08-20',
                'position': 'Midfielder',
                'age': 19,
                'contract_length': '1 year loan',
                'market_value': '€15M',
                'impact_rating': 6.0
            }
        ]

        return pd.DataFrame(dummy_transfers)

    def get_recent_transfers(self, days_back=30):
        """Get recent transfers within specified days"""
        all_transfers = self.get_dummy_transfer_data()

        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        all_transfers['date'] = pd.to_datetime(all_transfers['date'])

        recent_transfers = all_transfers[all_transfers['date'] >= cutoff_date]
        recent_transfers = recent_transfers.sort_values('date', ascending=False)

        return recent_transfers.to_dict('records')

    def get_team_transfers(self, team_name, transfer_type="all"):
        """Get transfers for specific team (in/out/all)"""
        all_transfers = self.get_dummy_transfer_data()

        if transfer_type == "in":
            team_transfers = all_transfers[all_transfers['to_team'].str.lower() == team_name.lower()]
        elif transfer_type == "out":
            team_transfers = all_transfers[all_transfers['from_team'].str.lower() == team_name.lower()]
        else:  # all
            team_transfers = all_transfers[
                (all_transfers['to_team'].str.lower() == team_name.lower()) |
                (all_transfers['from_team'].str.lower() == team_name.lower())
            ]

        return team_transfers.to_dict('records')

    def get_transfer_summary(self):
        """Get summary of transfer window activity"""
        all_transfers = self.get_dummy_transfer_data()

        # Extract fee values (simplified)
        total_spent = 0
        permanent_transfers = 0
        loans = 0

        for _, transfer in all_transfers.iterrows():
            if 'M' in transfer['fee']:
                try:
                    fee_value = float(transfer['fee'].split('€')[1].split('M')[0])
                    total_spent += fee_value
                except:
                    pass

            if transfer['transfer_type'] == 'Permanent':
                permanent_transfers += 1
            elif 'Loan' in transfer['transfer_type']:
                loans += 1

        summary = {
            'total_transfers': len(all_transfers),
            'permanent_transfers': permanent_transfers,
            'loan_transfers': loans,
            'estimated_total_spent': f"€{total_spent:.1f}M",
            'most_active_teams': {
                'buying': all_transfers['to_team'].value_counts().head(5).to_dict(),
                'selling': all_transfers['from_team'].value_counts().head(5).to_dict()
            },
            'by_position': all_transfers['position'].value_counts().to_dict(),
            'highest_fees': all_transfers.nlargest(3, 'impact_rating')[['player', 'from_team', 'to_team', 'fee']].to_dict('records'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return summary

    def get_team_strength_changes(self):
        """Analyze how transfers affect team strength"""
        all_transfers = self.get_dummy_transfer_data()

        team_changes = {}

        for team in self.serie_a_teams:
            transfers_in = all_transfers[all_transfers['to_team'] == team]
            transfers_out = all_transfers[all_transfers['from_team'] == team]

            impact_in = transfers_in['impact_rating'].sum() if not transfers_in.empty else 0
            impact_out = transfers_out['impact_rating'].sum() if not transfers_out.empty else 0

            net_impact = impact_in - impact_out

            team_changes[team] = {
                'transfers_in': len(transfers_in),
                'transfers_out': len(transfers_out),
                'impact_in': impact_in,
                'impact_out': impact_out,
                'net_impact': net_impact,
                'strength_change': 'Improved' if net_impact > 2 else 'Weakened' if net_impact < -2 else 'Stable'
            }

        # Sort by net impact
        sorted_changes = dict(sorted(team_changes.items(), key=lambda x: x[1]['net_impact'], reverse=True))

        return sorted_changes

if __name__ == "__main__":
    scraper = TransferDataScraper()

    print("=== Testing Transfer Data Scraper ===")

    # Test transfer summary
    summary = scraper.get_transfer_summary()
    print(f"\nTransfer Window Summary:")
    print(f"Total transfers: {summary['total_transfers']}")
    print(f"Estimated spending: {summary['estimated_total_spent']}")
    print(f"Most active buyers: {list(summary['most_active_teams']['buying'].keys())[:3]}")

    # Test team-specific transfers
    juve_transfers = scraper.get_team_transfers('Juventus')
    print(f"\nJuventus transfers: {len(juve_transfers)}")
    for transfer in juve_transfers:
        direction = "IN" if transfer['to_team'] == 'Juventus' else "OUT"
        print(f"  {direction}: {transfer['player']} - {transfer['fee']}")

    # Test team strength changes
    strength_changes = scraper.get_team_strength_changes()
    print(f"\nTeam strength changes:")
    for team, change in list(strength_changes.items())[:5]:
        print(f"  {team}: {change['strength_change']} (Net impact: {change['net_impact']:.1f})")

    # Test recent transfers
    recent = scraper.get_recent_transfers(60)
    print(f"\nRecent transfers: {len(recent)}")
    for transfer in recent[:3]:
        print(f"  {transfer['player']}: {transfer['from_team']} → {transfer['to_team']} ({transfer['fee']})")