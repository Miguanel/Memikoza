import json
import os
import requests
from flask import Flask, request, jsonify
from waitress import serve
from memenager import MemMenager
import logging
from dotenv import load_dotenv
app = Flask(__name__)

load_dotenv()
# Konfiguracja limitów
limits = [16, 11, 13, 11, 11, 11]
page_limits = {
    "jbzd_limit": limits[0],
    "jm_limit": limits[1],
    "dm_limit": limits[2],
    "kw_limit": limits[3],
    "rm_limit": limits[4],
    "ag_limit": limits[5]
}

@app.route('/')
def index():
    return "Serwer skrapujący Memikozy działa poprawnie!", 200


@app.route('/skrapuj-teraz')
def scrape_now():
    token = request.args.get('token')
    secret_token = os.environ.get('SECRET_TOKEN')
    gist_id = os.environ.get('GIST_ID')
    gh_token = os.environ.get('GITHUB_TOKEN')

    if token != secret_token:
        return jsonify({"error": "Brak dostępu"}), 403

    print("Pobieranie memów...")
    mm = MemMenager()
    mm.fresh_mems(page_limits, 0)

    # Konwersja daty na string dla JSON
    dane = mm.memy.copy()
    if "last_used" in dane:
        dane["last_used"] = dane["last_used"].strftime("%Y-%m-%d %H:%M:%S")

    # Wysyłka do GitHub Gist
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {"Authorization": f"token {gh_token}"}
    payload = {
        "files": {
            "memy.json": {"content": json.dumps(dane, indent=2)}
        }
    }

    req = requests.patch(url, json=payload, headers=headers)

    if req.status_code == 200:
        return jsonify({"status": "sukces", "message": "Gist zaktualizowany!"}), 200
    return jsonify({"status": "błąd", "details": req.text}), req.status_code

if __name__ == "__main__":
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    port = int(os.environ.get('PORT', 5000))
    print(f"Start serwera na porcie {port}")
    serve(app, host='0.0.0.0', port=port)