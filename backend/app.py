from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "RepoLens backend is alive"}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        if not data or "org" not in data:
            return jsonify({"error": "Request body must include 'org' key"}), 400

        org = data.get('org', '').strip()
        if not org:
            return jsonify({"error": "Organization name cannot be empty"}), 400

        print(f"[INFO] Analyzing organization: {org}")
        github_url = f'https://api.github.com/orgs/{org}/repos?type=public&per_page=5&sort=pushed'

        response = requests.get(github_url, headers=GITHUB_HEADERS)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from GitHub"}), response.status_code

        repos = response.json()
        report = []

        for repo in repos:
            repo_name = repo.get("name", "N/A")
            desc = repo.get("description") or "No description available."
            stars = repo.get("stargazers_count", 0)
            language = repo.get("language") or "N/A"
            url = repo.get("html_url", "#")

            report.append({
                "repo_name": repo_name,
                "description": desc,
                "stars": stars,
                "language": language,
                "github_url": url,
                "ai_summary": f"This repository focuses on {desc[:80]}..."
            })

        return jsonify({
            "message": f"Successfully analyzed {len(report)} repositories for '{org}'.",
            "report": report
        }), 200

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
