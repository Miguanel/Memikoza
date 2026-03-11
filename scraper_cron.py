import os
import requests
from memenager import MemMenager


def run_scraper():
    print("Uruchamiam skrapper Memikoza...")
    mm = MemMenager()

    # Limity z Twojego oryginalnego kodu [jbzd, jm, dm, kw, rm, ag]
    limits = [16, 11, 13, 11, 11, 11]
    page_limits = {
        "jbzd_limit": limits[0],
        "jm_limit": limits[1],
        "dm_limit": limits[2],
        "kw_limit": limits[3],
        "rm_limit": limits[4],
        "ag_limit": limits[5]
    }

    # Pobieramy memy (limit czasu 0, żeby wymusić odświeżenie)
    mm.fresh_mems(page_limits, 0)

    # Pobieramy zmienne środowiskowe z Render
    bin_id = os.environ.get('JSONBIN_BIN_ID')
    api_key = os.environ.get('JSONBIN_API_KEY')

    if not bin_id or not api_key:
        print("Błąd: Brak zmiennych środowiskowych JSONBIN_BIN_ID lub JSONBIN_API_KEY")
        return

    url = f'https://api.jsonbin.io/v3/b/{bin_id}'
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': api_key
    }

    print("Wysyłanie danych do JSONBin.io...")
    # PUT nadpisuje całego bina nowymi danymi
    req = requests.put(url, json=mm.memy, headers=headers)

    if req.status_code == 200:
        print("Pomyślnie zaktualizowano bazę memów!")
    else:
        print(f"Błąd zapisu: {req.status_code} - {req.text}")


if __name__ == "__main__":
    run_scraper()