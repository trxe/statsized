import argparse
import logging
import threading
import time
import datetime
import pytz
import polars as pl

import grpc_server.server as serve
import schedule
from data.tracker import get_scores_on_date, Tracker
from data.stores import Stores
from utils.logger import Slogger
from utils.metrics import OTLPMetrics

new_york_tz = pytz.timezone('America/New_York')

def parse_args():
    parser = argparse.ArgumentParser(
        prog="Time Series Data Server",
        description="Provides a gRPC interface to fetch or stream timeseries data of past/present NHL games",
    )
    parser.add_argument("-o", "--host", help="Host", default="localhost:50051")
    parser.add_argument("-c", "--config", help="config")
    return parser.parse_args()


def run_scheduler():
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            Slogger.log(f"Caught exception: {e}", logging.ERROR)
        time.sleep(1)

def game_updater():
    histogram = OTLPMetrics.get('games').create_histogram('events')
    Slogger.log("Finding NHL games")
    datestr = str(datetime.datetime.today().astimezone(new_york_tz)).split(' ')[0]
    score_sheet = get_scores_on_date(datestr)
    games = score_sheet['games']
    Slogger.log(f"Found games: {[g['id'] for g in games]}")
    for g in games:
        tracker = Tracker.poll_game(g['id'], g['goals'])
        Slogger.log(tracker)
        Stores.games_map[g['id']] = g
        for pid in Stores.team_id_map.get(tracker.away_id, {}).get('players'):
            schedule.every(1).seconds.do(lambda x: histogram.record(pid))
            player = Stores.players_map.get(pid)
            player_events = list(player.get('games', {}).get(g['id'], {}).get('events', {}).values())
            print(player['name'], player['positionCode'])
            print(pl.DataFrame(player_events))
    if not len(games):
        Slogger.log("No games found")

def main():
    args = parse_args()
    Slogger.init(__name__)
    Slogger.log("Started server")
    game_updater()
    schedule.every(30).seconds.do(game_updater)
    schedthred = threading.Thread(target=run_scheduler, daemon=True)
    schedthred.start()
    server = serve.server(args.host)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
