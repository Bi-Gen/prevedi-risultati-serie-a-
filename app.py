from flask import Flask, jsonify, request
import pandas as pd
import os
from data_fetcher import SerieADataFetcher
from injury_scraper import InjuryDataScraper
from transfer_scraper import TransferDataScraper
from prediction_engine import SerieAPredictionEngine
from fixtures_fetcher import SerieAFixturesFetcher

app = Flask(__name__)
data_fetcher = SerieADataFetcher()
injury_scraper = InjuryDataScraper()
transfer_scraper = TransferDataScraper()
fixtures_fetcher = SerieAFixturesFetcher()

# Initialize prediction engine (will load historical data)
print("Initializing prediction engine...")
prediction_engine = SerieAPredictionEngine(data_fetcher, injury_scraper, transfer_scraper)
print("Prediction engine ready!")

@app.route('/')
def home():
    return jsonify({
        "message": "Serie A Match Predictor API",
        "status": "active",
        "version": "0.1.0",
        "endpoints": {
            "/health": "Health check",
            "/api/matches": "Get Serie A matches (single season)",
            "/api/teams": "Get Serie A teams (single season)",
            "/api/matches/recent": "Get recent matches",
            "/api/seasons": "Get statistics from multiple seasons",
            "/api/matches/multi-season": "Get matches from multiple seasons",
            "/api/injuries": "Get current injury data",
            "/api/injuries/team/<team>": "Get injuries for specific team",
            "/api/transfers": "Get recent transfer data",
            "/api/transfers/team/<team>": "Get transfers for specific team",
            "/api/fixtures": "Get upcoming Serie A fixtures",
            "/api/fixtures/next-round": "Get next matchday fixtures",
            "/api/predict/<home>/<away>": "Predict specific match",
            "/api/predictions": "Get predictions for upcoming matches"
        },
        "supported_seasons": {
            "2023-24": "Historical data (Football-CSV)",
            "2024-25": "Complete season (DataHub)",
            "2025-26": "Current season (OpenFootball)"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/matches')
def get_matches():
    try:
        season = request.args.get('season', '2023-24')
        matches_df = data_fetcher.fetch_season_data(season)

        # Convert DataFrame to JSON-serializable format
        matches = matches_df.to_dict('records')

        stats = data_fetcher.get_basic_stats(matches_df)

        return jsonify({
            "season": season,
            "total_matches": len(matches),
            "stats": stats,
            "matches": matches
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/matches/recent')
def get_recent_matches():
    try:
        limit = int(request.args.get('limit', 10))
        season = request.args.get('season', '2023-24')

        matches_df = data_fetcher.fetch_season_data(season)
        recent_matches = matches_df.head(limit).to_dict('records')

        return jsonify({
            "limit": limit,
            "matches": recent_matches
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams')
def get_teams():
    try:
        season = request.args.get('season', '2023-24')
        matches_df = data_fetcher.fetch_season_data(season)

        teams = data_fetcher.get_teams(matches_df)

        return jsonify({
            "season": season,
            "total_teams": len(teams),
            "teams": teams
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/seasons')
def get_multiple_seasons():
    try:
        # Get seasons from query params or use defaults
        seasons_param = request.args.get('seasons', '2023-24,2024-25,2025-26')
        seasons = [s.strip() for s in seasons_param.split(',')]

        # Get combined data from multiple seasons
        combined_df = data_fetcher.get_multiple_seasons_data(seasons)

        # Get stats per season
        season_stats = {}
        for season in seasons:
            season_data = combined_df[combined_df['Season'] == season] if 'Season' in combined_df.columns else combined_df
            if not season_data.empty:
                season_stats[season] = {
                    "total_matches": len(season_data),
                    "home_wins": len(season_data[season_data['FTR'] == 'H']) if 'FTR' in season_data.columns else 0,
                    "away_wins": len(season_data[season_data['FTR'] == 'A']) if 'FTR' in season_data.columns else 0,
                    "draws": len(season_data[season_data['FTR'] == 'D']) if 'FTR' in season_data.columns else 0
                }

        return jsonify({
            "seasons": seasons,
            "total_matches_all_seasons": len(combined_df),
            "season_breakdown": season_stats,
            "data_sources": {
                "2023-24": "Football-CSV (Historical)",
                "2024-25": "DataHub (Complete Season)",
                "2025-26": "OpenFootball JSON (Current Season)"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/matches/multi-season')
def get_multi_season_matches():
    try:
        # Get parameters
        seasons_param = request.args.get('seasons', '2024-25,2025-26')
        seasons = [s.strip() for s in seasons_param.split(',')]
        limit = int(request.args.get('limit', 50))

        # Get combined data
        combined_df = data_fetcher.get_multiple_seasons_data(seasons)

        # Get recent matches across all seasons
        matches = combined_df.head(limit).to_dict('records')

        return jsonify({
            "seasons": seasons,
            "limit": limit,
            "total_available": len(combined_df),
            "matches": matches
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/injuries')
def get_injuries():
    try:
        # Get injury summary and detailed data
        summary = injury_scraper.get_injury_summary()
        impact = injury_scraper.get_availability_impact()

        return jsonify({
            "summary": summary,
            "team_impact": impact,
            "data_source": "Multiple injury tracking websites",
            "note": "Currently using realistic dummy data for demonstration"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/injuries/team/<team>')
def get_team_injuries(team):
    try:
        team_injuries = injury_scraper.get_team_injuries(team)

        return jsonify({
            "team": team,
            "total_injuries": len(team_injuries),
            "injuries": team_injuries,
            "last_updated": injury_scraper.get_injury_summary()["last_updated"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transfers')
def get_transfers():
    try:
        # Get transfer summary and recent activity
        summary = transfer_scraper.get_transfer_summary()
        recent_transfers = transfer_scraper.get_recent_transfers(days_back=60)
        strength_changes = transfer_scraper.get_team_strength_changes()

        return jsonify({
            "summary": summary,
            "recent_transfers": recent_transfers,
            "team_strength_changes": strength_changes,
            "data_source": "Transfer market websites",
            "note": "Currently using realistic dummy data based on actual 2024 summer window"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transfers/team/<team>')
def get_team_transfers(team):
    try:
        transfer_type = request.args.get('type', 'all')  # in/out/all
        team_transfers = transfer_scraper.get_team_transfers(team, transfer_type)

        return jsonify({
            "team": team,
            "transfer_type": transfer_type,
            "total_transfers": len(team_transfers),
            "transfers": team_transfers,
            "last_updated": transfer_scraper.get_transfer_summary()["last_updated"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prediction-factors')
def get_prediction_factors():
    try:
        # Combine all data sources for comprehensive view
        injury_summary = injury_scraper.get_injury_summary()
        transfer_summary = transfer_scraper.get_transfer_summary()
        injury_impact = injury_scraper.get_availability_impact()
        strength_changes = transfer_scraper.get_team_strength_changes()

        # Create combined view for each team
        team_factors = {}

        # Get unique teams from both sources
        teams_with_injuries = {impact['team'] for impact in injury_impact}
        teams_with_transfers = set(strength_changes.keys())
        all_teams = teams_with_injuries.union(teams_with_transfers)

        for team in all_teams:
            # Find team data in both sources
            team_injury_data = next((impact for impact in injury_impact if impact['team'] == team),
                                   {'team': team, 'impact_score': 0, 'players_out': 0, 'players_doubtful': 0})

            team_transfer_data = strength_changes.get(team,
                                   {'net_impact': 0, 'strength_change': 'Stable', 'transfers_in': 0, 'transfers_out': 0})

            team_factors[team] = {
                'injury_impact': team_injury_data['impact_score'],
                'players_unavailable': team_injury_data['players_out'] + team_injury_data['players_doubtful'],
                'transfer_impact': team_transfer_data['net_impact'],
                'squad_changes': team_transfer_data['transfers_in'] + team_transfer_data['transfers_out'],
                'overall_form_factor': team_transfer_data['net_impact'] - team_injury_data['impact_score'],
                'prediction_adjustment': 'Positive' if team_transfer_data['net_impact'] > team_injury_data['impact_score'] + 2
                                       else 'Negative' if team_transfer_data['net_impact'] < team_injury_data['impact_score'] - 2
                                       else 'Neutral'
            }

        return jsonify({
            "team_factors": team_factors,
            "summary": {
                "total_injuries": injury_summary['total_injuries'],
                "total_transfers": transfer_summary['total_transfers'],
                "most_affected_by_injuries": injury_impact[:3],
                "biggest_squad_changes": list(strength_changes.keys())[:3]
            },
            "note": "Combined injury and transfer data for match prediction enhancement"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fixtures')
def get_fixtures():
    try:
        days_ahead = int(request.args.get('days', 14))
        fixtures = fixtures_fetcher.get_upcoming_fixtures(days_ahead)

        return jsonify({
            "days_ahead": days_ahead,
            "total_fixtures": len(fixtures),
            "fixtures": fixtures
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fixtures/next-round')
def get_next_round():
    try:
        next_round = fixtures_fetcher.get_next_round_fixtures()

        return jsonify({
            "next_round": next_round,
            "total_matches": len(next_round),
            "matchday": next_round[0]['matchday'] if next_round else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict/<home>/<away>')
def predict_match(home, away):
    try:
        # Generate prediction for specific match
        prediction = prediction_engine.predict_match(home, away)

        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predictions')
def get_predictions():
    try:
        days_ahead = int(request.args.get('days', 7))
        prediction_type = request.args.get('type', 'all')  # all, big_matches, next_round

        predictions = []

        if prediction_type == 'next_round':
            fixtures = fixtures_fetcher.get_next_round_fixtures()
        elif prediction_type == 'big_matches':
            fixtures = fixtures_fetcher.get_big_matches(days_ahead)
        else:  # all
            fixtures = fixtures_fetcher.get_upcoming_fixtures(days_ahead)

        # Generate predictions for each fixture
        for fixture in fixtures[:10]:  # Limit to 10 to avoid timeouts
            try:
                prediction = prediction_engine.predict_match(
                    fixture['home_team'],
                    fixture['away_team']
                )

                # Add fixture info to prediction
                prediction['fixture_info'] = {
                    'date': fixture['date'],
                    'time': fixture.get('time', ''),
                    'round': fixture.get('round', ''),
                    'days_from_now': fixture['days_from_now']
                }

                predictions.append(prediction)

            except Exception as pred_error:
                print(f"Error predicting {fixture['home_team']} vs {fixture['away_team']}: {pred_error}")
                continue

        return jsonify({
            "prediction_type": prediction_type,
            "days_ahead": days_ahead,
            "total_predictions": len(predictions),
            "predictions": predictions,
            "generated_at": prediction_engine.historical_data.iloc[0]['Season'] if not prediction_engine.historical_data.empty else "No data"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predictions/big-matches')
def get_big_match_predictions():
    try:
        big_matches = fixtures_fetcher.get_big_matches(14)
        predictions = []

        for match in big_matches[:5]:  # Limit big matches
            try:
                prediction = prediction_engine.predict_match(
                    match['home_team'],
                    match['away_team']
                )

                prediction['fixture_info'] = match
                predictions.append(prediction)

            except Exception as pred_error:
                print(f"Error predicting big match: {pred_error}")
                continue

        return jsonify({
            "big_match_predictions": predictions,
            "total_predictions": len(predictions)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)