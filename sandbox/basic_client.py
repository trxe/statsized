import argparse
import requests
import yaml
import json
import logging
import datetime
import pytz
from data_fetcher import get_play_by_play_link
import time
import psycopg


conn = psycopg.connect(f"dbname=nhl user=trxe")
                
NHL_SCHEDULE_URL = "https://api-web.nhle.com/v1/schedule/"

def pull_week_schedule(date = "now", ignore_future = True):
    date = "now" if not date else str(date).split(' ')[0]
    nhl_week = requests.get(f"{NHL_SCHEDULE_URL}{date}").json()
    game_week = nhl_week.get('gameWeek')
    games = [
        g.get('id')
        for day in game_week
        for g in day.get('games', [])
        if not ignore_future 
            or datetime.datetime.fromisoformat(g.get('startTimeUTC').replace('Z', '')).astimezone(pytz.utc) < datetime.datetime.now().astimezone(pytz.utc)
    ]
    nhl_week['games'] = games
    return nhl_week

def main(config):
    metrics_url = f"{config.get('server').get('protocol')}{config.get('server').get('host')}:{config.get('server').get('port')}"
    start_date = None
    szn_start_date = None
    while not szn_start_date or start_date > szn_start_date:
        current_week = pull_week_schedule(start_date)
        start_date = datetime.datetime.fromisoformat(current_week.get('previousStartDate'))
        szn_start_date = datetime.datetime.fromisoformat(current_week.get('preSeasonStartDate'))
        if not szn_start_date or not start_date:
            logging.error(f"Broken response: {current_week}")
        games = current_week.get('games', [])
        print(start_date, szn_start_date, games)
        for game in games:
            result = conn.execute(f"SELECT COUNT(*) FROM plays WHERE game_id = {game}")
            count = result.fetchone()[0]
            if count:
                print(f"Already populated: {game} ({count} plays)")
                continue
            print(f"Sending: {game}")
            response = requests.post(metrics_url, params={
                'game_id':  game,
                'data_type':  "play-by-play",
                # 'data_type':  "shifts",
                'actions': [
                    # 'teams',
                    # 'players',
                    'roster',
                    'plays',
                    # 'shifts',
                ]
            } )
            print(response.text)
            js = json.loads(response.text)
            print(js)
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-c",
        "--config",
        default="config.yml",
        help="Contains the server host and port",
    )
    args = parser.parse_args()
    with open(args.config) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)
    # response = requests.get(hostname, params={
    #     'game': 2024190004
    # })
    # print(response.text)
    main(config)