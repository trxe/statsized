import argparse
import time
import logging
import schedule
import threading
from utils.logger import Slogger
from data.tracker import schedule_upcoming_games
from data.parser import Parser
import grpc_server.server as serve

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
    Slogger.log("Finding NHL games")
    games = [Parser.game(x) for x in schedule_upcoming_games("now")]
    for game in games:
        print(game.get('id'))
    if not len(games):
        Slogger.log("No games found")


def main():
    args = parse_args()
    Slogger.init(__name__)
    Slogger.log("Started server")
    schedule.every(5).seconds.do(game_updater)
    schedthred = threading.Thread(target=run_scheduler, daemon=True)
    schedthred.start()
    server = serve.server(args.host)
    server.wait_for_termination()

if __name__ == "__main__":
    main()
