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
            "/api/matches": "Get Serie A matches",
            "/api/teams": "Get Serie A teams",
            "/api/matches/recent": "Get recent matches"
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)