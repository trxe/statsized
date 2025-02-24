import logging
import time
import requests

ENV = "PROD"

APIWEB = "https://api-web.nhle.com/v1/" if ENV == 'PROD' else "localhost:8000/"
API = "https://api.nhle.com/stats/rest/en/" if ENV == 'PROD' else "localhost:8000/"

def fetch_data(url: str, params: map = {}):
    try:
        data = requests.get(url, params=params, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Referer': 'https://www.nhl.com/',
        }).json()
        time.sleep(1)
        return data
    except Exception as e:
        raise Exception(f"Error GET[{url}]: {e}")


def get_landing(game_id):
    landing_url = f"{APIWEB}gamecenter/{game_id}/landing"
    return fetch_data(landing_url)


def get_play_by_play(game_id):
    pbp_url = f"{APIWEB}gamecenter/{game_id}/play-by-play"
    return fetch_data(pbp_url)

def get_play_by_play_link(game_id):
    pbp_url = f"{APIWEB}gamecenter/{game_id}/play-by-play"
    return pbp_url


def get_shiftcharts(game_id, start_from="00:00"):
    shifts_url = f"{API}shiftcharts"
    shifts_params = {
        "cayenneExp": f'gameId={game_id} and startTime >= "{start_from}"',
        # "sort": str([{"property":"period", "direction": "ASC"},{"property":"startTime","direction":"ASC"}])
    }
    return fetch_data(shifts_url, shifts_params)


def get_scores_on_date(date: str = "now"):
    score_url = f"{APIWEB}score/{date}"
    return fetch_data(score_url)