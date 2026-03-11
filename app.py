import os
import requests
from flask import Flask, request, jsonify
from waitress import serve
from memenager import MemMenager
import logging

app = Flask(__name__)

# Konfiguracja limitów z Twojego oryginalnego kodu
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
    # Zwykły komunikat, żeby było widać, że serwer działa
    return "Serwer skrapujący Memikozy działa poprawnie!", 200


@app.route('/skrapuj-teraz')
def scrape_now():
    # Proste zabezpieczenie, żeby nikt obcy nie zajechał Ci serwera
    # Pobierze token z URL: /skrapuj-teraz?token=TWOJE_HASLO
    token = request.args.get('token')
    secret_token = os.environ.get('SECRET_TOKEN', 'domyslne_haslo_123')

    if token != secret_token:
        return jsonify({"error": "Brak dostępu. Zły token."}), 403

    print("Rozpoczynam pobieranie memów...")
    mm = MemMenager()
    mm.fresh_mems(page_limits, 0)  # 0 wymusza odświeżenie

    # Zmienne środowiskowe z JSONBin
    bin_id = os.environ.get('JSONBIN_BIN_ID')
    api_key = os.environ.get('JSONBIN_API_KEY')

    if not bin_id or not api_key:
        return jsonify({"error": "Brak konfiguracji JSONBin w zmiennych środowiskowych."}), 500

    # Wysłanie do bazy JSONBin.io
    url = f'https://api.jsonbin.io/v3/b/{bin_id}'
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': api_key
    }

    req = requests.put(url, json=mm.memy, headers=headers)

    if req.status_code == 200:
        return jsonify({"status": "sukces", "message": "Baza zaktualizowana!"}), 200
    else:
        return jsonify({"status": "błąd", "details": req.text}), req.status_code


if __name__ == "__main__":
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.DEBUG)
    # Na Renderze aplikacja musi nasłuchiwać na 0.0.0.0 i porcie ze zmiennej środowiskowej
    port = int(os.environ.get('PORT', 5000))
    serve(app, host='0.0.0.0', port=port)