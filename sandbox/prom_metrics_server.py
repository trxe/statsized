import datetime
import argparse
import schedule
import logging
import threading
import os
import re
import urllib.parse as urlparse
import yaml
import queue
import data_fetcher
import pytz
from metrics import PrometheusMetrics
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.DEBUG)
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
    game_queue = queue.SimpleQueue()

    @classmethod
    def setup(cls):
        # cls.beater_counter = PrometheusMetrics.create_counter('statsized', "beater_counter", '', "test")
        cls.game_counter = PrometheusMetrics.create_counter('statsized', "game_counter", '', "test")
        cls.team_standings = PrometheusMetrics.create_counter('statsized', "team_standings", '', "")
        # cls.game_gauge = PrometheusMetrics.create_gauge('statsized', "game_gauge", '', "test")
        # cls.game_histogram = PrometheusMetrics.create_histogram('statsized', "game_histogram", '', "test")

    @classmethod
    def heartbeat(cls):
        logger.debug("heartbeat")

    @classmethod
    def poll_game(cls):
        logger.debug("poll_game")
        try:
            game_id = cls.game_queue.get_nowait()
            landing = data_fetcher.get_landing(game_id)
            local_time = compute_start_time_local(landing)
            logger.info(f"Processing game: {game_id}")
            game_summary = {
                'game': game_id,
                'home_team': landing['homeTeam']['abbrev'],
                'home_team_score': landing['homeTeam'].get('score', None),
                'home_team_sog': landing['homeTeam'].get('sog', None),
                'datetime': local_time,
                'is_matinee': local_time.time() < datetime.time(18, 0),
                'away_team': landing['awayTeam']['abbrev'],
                'away_team_score': landing['awayTeam'].get('score', None),
                'away_team_sog': landing['awayTeam'].get('sog', None),
                'end_period': landing['periodDescriptor'].get('number'),
                'end_period_type': landing['periodDescriptor'].get('periodType'),
            }
            cls.game_counter.add(1, attributes=game_summary)
            points = compute_game_pts(game_summary)
            for (team, delta) in points:
                cls.team_standings.add(delta, {
                    'team': team,
                    'game': game_id,
                    'datetime': datetime
                })
        except queue.Empty:
            logger.info(f"No games queued")

    @classmethod
    def push_game(cls, game_id):
        cls.game_queue.put(game_id)
        logger.info(f"Queued game: {game_id}")

class NHLMetricsServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    
    def _parse_url_params(self, params):
        game = re.match("game=(\d*)", params).groups()
        game = game[0] if game else None
        return {
            'game': game,
            'request': params
        }

    def _enc(self, content):
        return str(content).encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        url = urlparse.urlparse(self.path)
        response = self._parse_url_params(url.query)
        MetricsApp.push_game(response.get('game'))
        self.wfile.write(self._enc(response))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        url = urlparse.urlparse(self.path)
        print(url)
        response = self._parse_url_params(url.query)
        MetricsApp.push_game(response.get('game'))
        self.wfile.write(self._enc(response))

def scheduler():
    while True:
        # try:
        schedule.run_pending()
        # except Exception as e:
        #     logger.error(f"Caught exception: {e}")

def run_server(ServerClass=HTTPServer, HandlerClass=NHLMetricsServer, config={}):
    server_config = config.get('server', {})
    server_host = server_config.get('host', 'localhost')
    server_port = server_config.get('port', '3871')
    prom_config = config.get('prometheus', {})
    httpd = ServerClass(
        (server_host, server_port), 
        HandlerClass
    )

    # Start metrics
    PrometheusMetrics.start(
        prom_config.get('host', 'localhost'), 
        prom_config.get('port', '9464'),
        prom_config.get('service_name', 'nhl-metrics'),
    )
    MetricsApp.setup()
    
    # Job schedule
    schedule.every(5).seconds.do(MetricsApp.poll_game)
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