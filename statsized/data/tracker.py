import logging
import time
import requests
from utils.error import NetworkException
from utils.logger import Slogger
from data.stores import Stores

ENV = "DEV"

APIWEB = "https://api-web.nhle.com/v1/" if ENV == 'PROD' else "localhost:8000"
API = "https://api.nhle.com/stats/rest/en/" if ENV == 'PROD' else "localhost:8000"

def fetch_data(url: str, params: map = {}):
    Slogger.log(f"Pulling from : {url}")
    try:
        data = requests.get(url, params=params, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Referer': 'https://www.nhl.com/',
        }).json()
        time.sleep(1)
        return data
    except Exception as e:
        raise NetworkException(f"Error GET[{url}]: {e}")


def get_landing(game_id):
    landing_url = f"{APIWEB}gamecenter/{game_id}/landing"
    return fetch_data(landing_url)


def get_play_by_play(game_id):
    pbp_url = f"{APIWEB}gamecenter/{game_id}/play-by-play"
    return fetch_data(pbp_url)


def get_shiftcharts(game_id, start_from="00:00"):
    shifts_url = f"{API}shiftcharts"
    shifts_params = {
        "cayenneExp": f'gameId={game_id} and startTime >= "{start_from}"',
    }
    return fetch_data(shifts_url, shifts_params)


def get_scores_on_date(date: str = "now"):
    score_url = f"{APIWEB}score/{date}"
    try:
        return fetch_data(score_url)
    except NetworkException as e:
        Slogger.log(e, logging.ERROR)

class Tracker:
    by_game = {}

    @classmethod
    def poll_game(cls, game_id, goals=[]):
        Slogger.log(f"Polling {game_id}")
        if not cls.by_game.get(game_id):
            cls.by_game[game_id] = Tracker(game_id)
        tracker = cls.by_game.get(game_id)
        tracker._set_state(game_id)
        tracker._set_goals(game_id, goals)
        return tracker

    def _handle_shift(self, shift):
        pid = shift['playerId']
        Stores.players_map[pid]['games'].get(self.game_id)['shifts'][shift['id']] = shift

    def _handle_play(self, play):
        # only handles goals rn
        pid_fields = [
            'scoringPlayerId',
            'assist1PlayerId',
            'assist2PlayerId',
            'playerId',
            'losingPlayerId',
            'winningPlayerId',
        ]
        for field in pid_fields:
            pid = play.get('details', {}).get(field)
            if not pid:
                continue
            if self.last_sort_order < play['sortOrder']:
                self.last_sort_order = play['sortOrder']
            Stores.players_map[pid]['games'].get(self.game_id)['events'][play['eventId']] = play
        return play
    
    def _set_state(self, game_id):
        # Get current state of play
        Slogger.log(f"Updating {game_id}")
        pbp = get_play_by_play(game_id)
        Slogger.log(f"PBP {game_id}")
        shifts = get_shiftcharts(game_id)
        Slogger.log(f"Shifts {game_id}")
        # if not yet initialized
        if not self.clock:
            pbp['awayTeam']['players'] = set()
            pbp['homeTeam']['players'] = set()
            Stores.team_id_map[pbp['awayTeam'].get('id')] = pbp['awayTeam']
            Stores.team_id_map[pbp['homeTeam'].get('id')] = pbp['homeTeam']
            Stores.team_abbrev_to_id[pbp['awayTeam'].get('abbrev')] = pbp['awayTeam']['id']
            Stores.team_abbrev_to_id[pbp['homeTeam'].get('abbrev')] = pbp['homeTeam']['id']
            self.away_abbrev = pbp['awayTeam'].get('abbrev')
            self.home_abbrev = pbp['homeTeam'].get('abbrev')
            self.away_id = pbp['awayTeam'].get('id')
            self.home_id = pbp['homeTeam'].get('id')
        if not Stores.games_map.get(game_id):
            Stores.games_map[game_id] = {
                'shifts': shifts['data'],
                'events': pbp['plays']
            }
        for player in pbp['rosterSpots']:
            pid = player.get('playerId')
            tid = player.get('teamId')
            if not Stores.players_map.get(pid):
                Stores.players_map[pid] = player
                player['games'] = { }
                player['name'] = f"{player['firstName']['default']} {player['lastName']['default']}",
                Stores.team_id_map.get(tid)['players'].add(pid)
            if not Stores.players_map[pid]['games'].get(game_id): 
                Stores.players_map[pid]['games'][game_id] = {
                    'shifts': {},
                    'events': {},
                }
        for play in pbp['plays']:
            self._handle_play(play)
        for shift in shifts['data']:
            self._handle_shift(shift)
        self.clock = pbp['clock']
    
    def _set_goals(self, game_id, goals):
        self.away_goals = [g for g in goals if g['teamAbbrev'] == self.away_abbrev]
        self.home_goals = [g for g in goals if g['teamAbbrev'] == self.home_abbrev]

    def __init__(self, game_id):
        self.game_id = game_id
        self.clock = {}
        self.last_start_time = ""
        self.away_goals = []
        self.home_goals = []
        self.last_sort_order = -1
    
    def __str__(self):
        return f"""
            Clock: {self.clock}; Score: {self.away_abbrev} {len(self.away_goals)} - {self.home_abbrev} {len(self.home_goals)}
            Away: {[{
                'name': g['name']['default'],
                'assists': [gx['name']['default'] for gx in g['assists']],
                'period': g['period'],
                'time': g['timeInPeriod'],
            } for g in self.away_goals]}
            Home: {[{
                'name': g['name']['default'],
                'assists': [gx['name']['default'] for gx in g['assists']],
                'period': g['period'],
                'time': g['timeInPeriod'],
            } for g in self.home_goals]}
        """