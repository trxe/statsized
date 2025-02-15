import requests
from utils.logger import Slogger
import logging

NHLE = "https://api-web.nhle.com/v1/"

class Tracker:
    def __init__(self, game_id):
        print(game_id)
        pass

    def poll_game(self):
        pass

    def poll_game_events(self):
        pass

    def poll_game_shifts(self):
        pass

def schedule_upcoming_games(date: str = "now") -> list[Tracker]:
    SCORE_URL = f"{NHLE}score/{date}"
    Slogger.log(f"Pulling games from : {SCORE_URL}")
    try:
        full_info = requests.get(SCORE_URL).json()
        return full_info.get('games', [])
    except Exception as e:
        Slogger.log(f"Error GET[{SCORE_URL}]: {e}", logging.ERROR)
        return []
    # returns a list of Trackers whose creation is scheduled
    # return []