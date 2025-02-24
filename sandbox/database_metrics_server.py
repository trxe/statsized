import datetime
import argparse
import schedule
import logging
import threading
import json
import os
import re
import urllib.parse as urlparse
import yaml
import queue
import data_fetcher
import pytz
from database import PostgreSQLDB
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logging.getLogger('schedule').setLevel(logging.ERROR)
logger = logging.getLogger("statsized")

def compute_start_time_local(landing):
    startutc = datetime.datetime.fromisoformat(landing['startTimeUTC'].replace("Z", "+00:00"))
    venue_tz = pytz.timezone(landing['venueTimezone'])
    return startutc.astimezone(venue_tz)

def compute_game_pts(summary):
    diff = summary.get('home_team_score') - summary.get('away_team_score')
    period = summary.get('end_period_type')
    (winner, loser) = ('away_team', 'home_team') if diff < 0 else ('home_team', 'away_team')
    return [
        (summary.get(winner), 2),
        (summary.get(loser), 0 if period == 'REG' else 1)
    ]

class MetricsApp:
    games_table_keys = [
                        ["game_id", "SERIAL PRIMARY KEY"],
                        ["home_team", "VARCHAR(3)"],
                        ["home_team_score", "INT"],
                        ["home_team_sog", "INT"],
                        ["away_team", "VARCHAR(3)"],
                        ["away_team_score", "INT"],
                        ["away_team_sog", "INT"],
                        ["datetime", "TIMESTAMP"],
                        ["is_matinee", "BOOLEAN"],
                        ["end_period", "INT"],
                        ["end_period_type", "VARCHAR(3)"],
                    ]
    teams_table_keys = [
                        ["team_id", "INT PRIMARY KEY"],
                        ["name", "TEXT"],
                        ["abbrev", "TEXT"],
                        ["place_name", "TEXT"],
                        ["logo", "TEXT"],
                        ["darkLogo", "TEXT"],
                    ]
    players_table_keys = [
                        ["player_id", "INT PRIMARY KEY"],
                        ["team_id", "INT"],
                        ["first_name", "VARCHAR(40)"],
                        ["last_name", "VARCHAR(40)"],
                    ]
    roster_table_keys = [
                        ["player_id", "INT PRIMARY KEY"],
                        ["team_id", "INT"],
                        ["game_id", "INT"],
                        ["jersey_number", "INT"],
                        ["position", "VARCHAR(3)"],
                        ["UNIQUE", "(player_id, game_id)"],
                    ]
    events_table_keys = [ 
                        ["game_id", "INT"],
                        ["event_id", "INT"],
                        ["event", "VARCHAR(20)"],
                        ["situation", "VARCHAR(4)"],
                        ["time", "TIME"],
                        ["time_left", "TIME"],
                        ["period", "INT"],
                        ["x_coord", "INT"],
                        ["y_coord", "INT"],
                        ["zone_code", "VARCHAR(3)"],
                        ["shot_type", "VARCHAR(30)"],
                        ["event_owner_team_id", "INT"],
                        ["losing_player_id", "INT"],
                        ["winning_player_id", "INT"],
                        ["hitting_player_id", "INT"],
                        ["hittee_player_id", "INT"],
                        ["scoring_player_id", "INT"],
                        ["scoring_player_total", "INT"],
                        ["away_score", "INT"],
                        ["home_score", "INT"],
                        ["blocking_player_id", "INT"],
                        ["shooting_player_id", "INT"],
                        ["drawn_by_player_id", "INT"],
                        ["committed_by_player_id", "INT"],
                        ["goalie_in_net_id", "INT"],
                        ["player_id", "INT"],
                        ["penalty", "VARCHAR(30)"], # descKey
                        ["reason", "VARCHAR(50)"],
                        ["PRIMARY KEY(game_id, event_id)"],
                    ]
    shifts_table_keys = [ 
                        ["id", "INT PRIMARY KEY"],
                        ["game_id", "INT NOT NULL"],
                        ["team_id", "INT"],
                        ["player_id", "INT"],
                        ["shift_number", "INT"],
                        ["start_time", "TIME"],
                        ["end_time", "TIME"],
                        ["type_code", "INT"],
                        ["event_number", "INT"],
                        ["event_description", "VARCHAR(20)"],
                        ["event_details", "TEXT"],
                        ["period", "INT"],
                        ["duration_s", "INT"],
                    ]
    game_queue = queue.SimpleQueue()

    @classmethod
    def setup(cls):
        PostgreSQLDB.create_table('games', cls.games_table_keys)
        PostgreSQLDB.create_table('players', cls.players_table_keys)
        PostgreSQLDB.create_table('teams', cls.teams_table_keys)
        PostgreSQLDB.create_table('events', cls.events_table_keys)
        PostgreSQLDB.create_table('shifts', cls.shifts_table_keys)
        PostgreSQLDB.create_table('roster', cls.roster_table_keys)
        PostgreSQLDB.commit()
    
    @classmethod
    def _insert_game(cls, landing):
        game_id = landing['id']
        result = PostgreSQLDB.select("games", ["game_id"], f"WHERE game_id = {game_id}")
        if result.fetchone():
            logger.info(f"Already populated: {game_id}")
            return False
        local_time = compute_start_time_local(landing)
        logger.info(f"Processing game: {game_id}")
        game_summary = {
            'game_id': game_id,
            'home_team': landing['homeTeam']['abbrev'],
            'home_team_score': landing['homeTeam'].get('score', None),
            'home_team_sog': landing['homeTeam'].get('sog', None),
            'datetime': local_time,
            'is_matinee': local_time.time() < datetime.time(18, 0),
            'away_team': landing['awayTeam']['abbrev'],
            'away_team_score': landing['awayTeam'].get('score', None),
            'away_team_sog': landing['awayTeam'].get('sog', None),
            'end_period': landing.get('periodDescriptor', {}).get('number', None),
            'end_period_type': landing.get('periodDescriptor', {}).get('periodType', None),
        }
        result = PostgreSQLDB.insert("games", game_summary, ["game_id"])
        logger.info(result.fetchall())
        PostgreSQLDB.commit()
        return True

    @classmethod
    def _insert_players(cls, playbyplay):
        logger.info(f"Processing players: {playbyplay.get('id')}")
        players = playbyplay.get('rosterSpots', [])
        players_db = [
            {
                'player_id': p.get('playerId'),
                'team_id': p.get('teamId'), # currently dangerous. May not be latest.
                'first_name': p.get('firstName', {}).get('default'),
                'last_name': p.get('lastName', {}).get('default'),
            } for p in players
        ]
        PostgreSQLDB.insert_many('players', players_db, ['player_id'])
        PostgreSQLDB.commit()
        logger.info(f"Pushed players for: {playbyplay.get('id')}")
        return True

    @classmethod
    def _insert_roster(cls, playbyplay):
        logger.info(f"Processing roster: {playbyplay.get('id')}")
        roster = playbyplay.get('rosterSpots', [])
        roster_db = [
            {
                'player_id': p.get('playerId'),
                'team_id': p.get('teamId'),
                'game_id': playbyplay.get('id'),
                'jersey_number': p.get('sweaterNumber'),
                'position': p.get('positionCode'),
            } for p in roster
        ]
        PostgreSQLDB.insert_many('roster', roster_db, ['player_id', 'game_id'])
        PostgreSQLDB.commit()
        logger.info(f"Pushed roster for: {playbyplay.get('id')}")
        return True

    @classmethod
    def _insert_events(cls, playbyplay):
        logger.info(f"Processing events: {playbyplay.get('id')}")
        game_id = playbyplay.get('id')
        events = playbyplay.get('events', [])
        events_db = [
            {
                "game_id": game_id,
                "event_id": ev.get('eventId'),
                "team_id": ev.get('eventId'),
                "event_id": game_id,
            } for ev in events
        ]
        PostgreSQLDB.insert_many('events', events_db, ['player_id', 'team_'])
        PostgreSQLDB.commit()
        logger.info(f"Pushed events for: {playbyplay.get('id')}")
        return True

    @classmethod
    def _insert_teams(cls, playbyplay):
        logger.info(f"Processing teams: {playbyplay.get('id')}")
        teams = [
            playbyplay.get('homeTeam', {}),
            playbyplay.get('awayTeam', {}),
        ]
        teams_db = [
            {
                'team_id': t.get('id'),
                'name': t.get('commonName', {}).get('default'),
                'abbrev': t.get('abbrev'),
                'place_name': t.get('placeName', {}).get('default'),
                'logo': t.get('logo'),
                'darklogo': t.get('darkLogo'),
            } for t in teams
        ]
        PostgreSQLDB.insert_many('teams', teams_db, ['team_id'])
        PostgreSQLDB.commit()
        logger.info(f"Pushed teams for: {playbyplay.get('id')}")
        return True

    @classmethod
    def _insert_shifts(cls, shiftschart):
        logger.info(f"Processing shifts: {shiftschart.get('id')}")
        shifts = shiftschart.get('data', [])
        game_id = shiftschart.get('id')
        result = PostgreSQLDB.select("shifts", ["game_id"], f"WHERE game_id = {game_id}")
        if result.fetchone():
            logger.info(f"Already populated: {game_id}")
            return False
        def compute_seconds(durstr):
            if not durstr:
                return None
            return int(durstr[:2]) * 60 + int(durstr[3:])

        shifts_db = [
            {
                "id": s.get('id'),
                "game_id": s.get('gameId'),
                "team_id": s.get('teamId'),
                "player_id": s.get('playerId'),
                "start_time": s.get('startTime'),
                "end_time": s.get('endTime'),
                "shift_number": s.get('shiftNumber'),
                "type_code": s.get('typeCode'),
                "event_number": s.get('eventNumber'),
                "event_description": s.get('eventDescription'),
                "event_details": s.get('eventDetails'),
                "period": s.get('period'),
                "duration_s": compute_seconds(s.get('duration', ''))
            } for s in shifts
        ]
        PostgreSQLDB.insert_many('shifts', shifts_db, ['id'])
        PostgreSQLDB.commit()
        logger.info(f"Pushed shifts for: {game_id}")
        return True

    @classmethod
    def _get_game_data(cls, src, game_id):
        if src == 'play-by-play':
            return data_fetcher.get_play_by_play(game_id)
        if src == 'landing':
            return data_fetcher.get_landing(game_id)
        if src == 'shifts':
            charts = data_fetcher.get_shiftcharts(game_id)
            charts['id'] = game_id
            return charts

    @classmethod
    def poll_game(cls):
        logger.debug("poll_game")
        try:
            while True:
                request = cls.game_queue.get_nowait()
                game_id = request.get('game_id', [])
                if not game_id:
                    logger.info(f"request without game id: {request}")
                    continue
                data_type = request.get('data_type', [])
                if not data_type:
                    logger.info(f"request without data type: {request}")
                    continue
                game_data = cls._get_game_data(data_type[0], game_id[0])
                actions = request.get('actions', [])
                succ = False
                for action in actions:
                    if action == "landing":
                        succ = cls._insert_game(game_data) or succ
                    elif action == "events":
                        succ = cls._insert_events(game_data) or succ
                    elif action == "players":
                        succ = cls._insert_players(game_data) or succ
                    elif action == "roster":
                        succ = cls._insert_roster(game_data) or succ
                    elif action == "shifts":
                        succ = cls._insert_shifts(game_data) or succ
                    elif action == "teams": 
                        succ = cls._insert_teams(game_data) or succ
                    else:
                        logger.error(f"Unrecognised command: {action}")
                if succ:
                    break
        except queue.Empty:
            logger.debug(f"No games queued")

    @classmethod
    def push_game(cls, request):
        cls.game_queue.put(request)
        logger.info(f"Queued : {request}")

class NHLMetricsServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    
    def _parse_url_params(self, params):
        parts = [x.split('=') for x in params.replace('?', '').split('&')]
        body = {}
        for param in parts:
            if not body.get(param[0]):
                body[param[0]] = []
            body[param[0]].append(''.join(param[1:]))
        print(params, parts, body)
        return body

    def _enc(self, content):
        return json.dumps(content).encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        queue_now = list(queue)
        self.wfile.write(self._enc(queue_now))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        url = urlparse.urlparse(self.path)
        body = self._parse_url_params(url.query)
        MetricsApp.push_game(body)
        response = {
            "actions_for_game": body.get('game_id', [])
        }
        self.wfile.write(self._enc(response))

def scheduler():
    while True:
        schedule.run_pending()

def run_server(ServerClass=HTTPServer, HandlerClass=NHLMetricsServer, config={}):
    server_config = config.get('server', {})
    server_host = server_config.get('host', 'localhost')
    server_port = server_config.get('port', '3871')
    db_config = config.get('postgres', {})
    httpd = ServerClass(
        (server_host, server_port), 
        HandlerClass
    )

    # Start metrics
    PostgreSQLDB.start(
        db_config.get('dbname', 'nhl'), 
        db_config.get('user', 'trxe'),
    )
    MetricsApp.setup()
    
    # Job schedule
    schedule.every(0.5).seconds.do(MetricsApp.poll_game)
    # schedule.every(1).seconds.do(MetricsApp.heartbeat)
    threading.Thread(target=scheduler, daemon=True).start()

    # Serve
    logger.info(f"Starting server at {server_host}:{server_port}")
    logger.info(f"File running from: {os.path.abspath(os.getcwd())}")
    httpd.serve_forever()
    return 

def parse_config():
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-c",
        "--config",
        default="config.yml",
        help="Contains the server host and port",
    )
    args =  parser.parse_args()
    with open(args.config) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)
            return {}

if __name__ == "__main__":
    run_server(config=parse_config())