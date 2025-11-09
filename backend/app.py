from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Backend awake"}), 200


app = Flask(__name__)

CCORS(app, resources={
    r"/*": {
        "origins": [
            "https://shreyyyansh.github.io",  # GitHub Pages
            "https://repolens-backend.onrender.com",  # Backend (Render)
            "http://localhost:5000",  # Local testing
            "http://127.0.0.1:5500"  # Local VS Code live server
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# check_at_last
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}


@app.route('/')
def home():
    """Simple root route to check if the backend is live"""
    return jsonify({"message": "✅ RepoLens Backend is running successfully!"})


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or "org" not in data:
            return jsonify({"error": "Request body must include 'org' key"}), 400

        org = data.get('org', '').strip()
        if not org:
            return jsonify({"error": "Organization name cannot be empty"}), 400

        print(f"[INFO] 🔍 Analyzing organization: {org}")

        github_url = f'https://api.github.com/orgs/{org}/repos?type=public&per_page=5&sort=pushed'

        response = requests.get(github_url, headers=GITHUB_HEADERS)
        if response.status_code == 404:
            return jsonify({"error": f"GitHub organization '{org}' not found."}), 404
        elif response.status_code == 403:
            return jsonify({
                "error": "GitHub rate limit exceeded. Please try again later or add a valid token."
            }), 429
        elif not response.ok:
            return jsonify({"error": f"GitHub API error: {response.text}"}), 500

        repos = response.json()
        if not isinstance(repos, list):
            print("[WARNING] Unexpected response:", repos)
            return jsonify({"error": "Unexpected API response format"}), 500

        report = []
        for repo in repos:
            repo_name = repo.get('name', 'N/A')
            desc = repo.get('description') or "No description available."
            stars = repo.get('stargazers_count', 0)
            language = repo.get('language') or "N/A"
            url = repo.get('html_url', '#')
            last_push = repo.get('pushed_at', 'Unknown')

            summary = f"This repository focuses on {desc[:80]}..."

            report.append({
                "repo_name": repo_name,
                "description": desc,
                "stars": stars,
                "language": language,
                "github_url": url,
                "last_push": last_push,
                "ai_summary": summary,
                "activity_status": "Active" if stars > 0 else "Inactive"
            })

        if not report:
            return jsonify({
                "message": f"No public repositories found for '{org}'.",
                "report": []
            }), 200

        return jsonify({
            "message": f"Successfully analyzed {len(report)} repositories for '{org}'.",
            "report": report
        }), 200

    except Exception as e:
        print("[CRITICAL ERROR]", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    print("[INFO] 🚀 Starting Flask backend server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
