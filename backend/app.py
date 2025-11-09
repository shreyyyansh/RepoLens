from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ------------------------------------------------------------
# 🔐 GitHub Token Configuration
# ------------------------------------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # ---------------------------
        # 1️⃣ Validate Request
        # ---------------------------
        data = request.get_json()
        if not data or "org" not in data:
            return jsonify({"error": "Request body must include 'org' key"}), 400

        org = data.get('org', '').strip()
        if not org:
            return jsonify({"error": "Organization name cannot be empty"}), 400

        print(f"[INFO] Analyzing organization: {org}")

        # ---------------------------
        # 2️⃣ GitHub API Call (Fetch Repositories)
        # ---------------------------
        github_url = f'https://api.github.com/orgs/{org}/repos?type=public&per_page=5&sort=pushed'

        try:
            response = requests.get(github_url, headers=GITHUB_HEADERS)
            response.raise_for_status()
            repos = response.json()

            # Ensure repos is a list (not error message)
            if not isinstance(repos, list):
                print("[WARNING] Unexpected GitHub response:", repos)
                raise ValueError("Unexpected API response format")

        except requests.exceptions.HTTPError as http_err:
            # Handle specific GitHub errors
            error_text = str(http_err)
            print(f"[ERROR] GitHub API error: {error_text}")

            # Rate limit issue
            if "403" in error_text and "rate limit" in error_text.lower():
                return jsonify({
                    "error": "GitHub rate limit exceeded. Wait a few minutes or set a valid token."
                }), 429

            # Org not found — attempt suggestion
            suggestions = []
            try:
                search_url = f"https://api.github.com/search/users?q={org}+type:org"
                search_resp = requests.get(search_url, headers=GITHUB_HEADERS)
                if search_resp.ok:
                    search_data = search_resp.json() or {}
                    items = search_data.get("items", [])
                    if isinstance(items, list):
                        suggestions = [i.get("login", "") for i in items if i.get("login")]
            except Exception as s_err:
                print("[ERROR] Failed to fetch suggestions:", s_err)

            return jsonify({
                "error": f"GitHub organization '{org}' not found.",
                "suggestions": suggestions
            }), 404

        except Exception as e:
            print("[ERROR] General GitHub API failure:", e)
            return jsonify({"error": f"GitHub API failed: {str(e)}"}), 500

        # ---------------------------
        # 3️⃣ Process Repository Data
        # ---------------------------
        report = []
        for repo in repos:
            if not isinstance(repo, dict):
                continue

            repo_name = repo.get('name', 'N/A')
            desc = repo.get('description') or "No description available."
            stars = repo.get('stargazers_count', 0)
            language = repo.get('language') or "N/A"
            url = repo.get('html_url', '#')

            summary = f"This repository focuses on {desc[:80]}..."

            report.append({
                "repo_name": repo_name,
                "description": desc,
                "stars": stars,
                "language": language,
                "github_url": url,
                "ai_summary": summary
            })

        if not report:
            return jsonify({
                "message": f"No public repositories found for '{org}'.",
                "report": []
            }), 200

        # ---------------------------
        # 4️⃣ Final Success Response
        # ---------------------------
        return jsonify({
            "message": f"Successfully analyzed {len(report)} repositories for '{org}'.",
            "report": report
        }), 200

    except Exception as e:
        print("[CRITICAL ERROR]", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ------------------------------------------------------------
# 🧩 App Entry Point
# ------------------------------------------------------------
if __name__ == '__main__':
    print("[INFO] Starting Flask backend server...")
    app.run(debug=True)
