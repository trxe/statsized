import argparse
import json
import datetime
import logging
import os
import pytz
import re
import schedule
import threading
import urllib.parse as urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

class Clock:
    clock = pytz.timezone('America/New_York').localize(datetime.datetime.now())

    @classmethod
    def set(cls, val):
        cls.clock = datetime.datetime.fromisoformat(val).astimezone(pytz.timezone('America/New_York'))
        print(cls.read())

    @classmethod
    def tick(cls):
        cls.clock += datetime.timedelta(seconds=1)
        print(cls.read())

    @classmethod
    def read(cls):
        return str(cls.clock)

class MockNHLServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _enc(self, content):
        return str(content).encode("utf8")  # NOTE: must return a bytes object!
    
    def _post_process(self, data, datatype):
        return data
    
    def _serve_game(self, game_id, datatype):
        fp = f"{os.getcwd()}/mock_source/data/{datatype}-{game_id}.json"
        try:
            with open(fp, 'r') as file:
                data = file.read()
            return self._post_process(data, datatype)
        except Exception as e:
            logging.error(e)
    
    def _serve_shifts(self, params):
        cayenne = [x for x in params if 'cayenne' in x]
        if not cayenne:
            return {}
        cayenne = cayenne[0]
        gameId = re.match("cayenneExp=.*gameId.*=(\d*).*", cayenne)
        if not gameId:
            return {'message': 'gameId not found'}
        gameId = gameId.group(1)
        duration = re.match("cayenneExp=.*duration.*=(\d*:\d*).*", cayenne)
        if not duration:
            return {'message': 'duration not found', 'gameId': gameId}
        duration = duration.group(1)
        return {
            'gameId': gameId,
            'duration': duration,
            'data': []
        }
        

    def do_GET(self):
        url = urlparse.urlparse(self.path)
        path_hierarchy = [x for x in url.path.split('/') if len(x)]
        queries = url.query.split('&')
        self._set_headers()
        response = {}
        print(path_hierarchy)
        if not len(path_hierarchy):
            response = {'message': "mock server for data"}
        elif path_hierarchy[0] == 'gamecenter' and len(path_hierarchy) == 3:
            logging.info(f"Loading gc: {self.path}")
            response = self._serve_game(path_hierarchy[1], path_hierarchy[2])
        elif path_hierarchy[0] == 'shiftcharts':
            logging.info(f"Loading shifts: {self.path}")
            response = self._serve_shifts(queries)
        self.wfile.write(self._enc(response))


    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(self._html("POST!"))

def setup_clock():
    schedule.every(1).seconds.do(Clock.tick)

def scheduler():
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.error(f"Caught exception: {e}")

def run(server_class=HTTPServer, handler_class=MockNHLServer, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    setup_clock()
    schedthred = threading.Thread(target=scheduler, daemon=True)
    schedthred.start()

    print(f"Starting httpd server on {addr}:{port}, from {os.path.abspath(os.getcwd())}")
    httpd.serve_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    parser.add_argument(
        "-t",
        "--time",
        type=str,
        default=str(datetime.datetime.astimezone(datetime.datetime.now())),
        help="mock time starting from",
    )
    args = parser.parse_args()
    Clock.set(args.time)
    run(addr=args.listen, port=args.port)