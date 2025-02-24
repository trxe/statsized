import argparse
import requests
import yaml
import logging
import datetime
import pytz
from data_fetcher import get_play_by_play_link
import time

NHL_SCHEDULE_URL = "https://api-web.nhle.com/v1/schedule/"

def pull_week_schedule(date = "now", exact = False):
    date = "now" if not date else str(date).split(' ')[0]
    nhl_week = requests.get(f"{NHL_SCHEDULE_URL}{date}").json()
    game_week = nhl_week.get('gameWeek')
    games = [
        g.get('id')
        for day in game_week
        for g in day.get('games', [])
        if not exact or day.get('date') == date
    ]
    nhl_week['games'] = games
    return nhl_week

def main(config):
    current_week = pull_week_schedule("2024-10-22", exact=True)
    games = current_week.get('games', [])
    for game in games:
        metrics_url = f"{config.get('server').get('protocol')}{config.get('server').get('host')}:{config.get('server').get('port')}"
        response = requests.post(metrics_url, params={
            'game_id':  game,
            # 'data_type':  "play-by-play",
            'data_type':  "play-by-play",
            'actions': [
                'teams',
                'players',
                # 'roster',
                # 'plays',
                # 'shifts',
            ]
        } )
        print(response.text)
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