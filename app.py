from flask import Flask, jsonify, request
import pandas as pd
import os
from data_fetcher import SerieADataFetcher

app = Flask(__name__)
data_fetcher = SerieADataFetcher()

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
            "/api/matches/multi-season": "Get matches from multiple seasons"
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)