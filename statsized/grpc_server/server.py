from concurrent.futures import ThreadPoolExecutor
import grpc
import grpc._server
import statsized_pb2
import statsized_pb2_grpc
from utils.logger import Slogger


class StatsizedServicer(statsized_pb2_grpc.StatsizedServicer):
    def GetCurrentGames(self, request, context):
        Slogger.log("GetCurrentGames")
        Slogger.log(request)

        response = statsized_pb2.Response()
        response.games = []
        return response


def server(hostport: str) -> grpc._server._Server:
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    statsized_pb2_grpc.add_StatsizedServicer_to_server(StatsizedServicer(), server)
    server.add_insecure_port(hostport)
    server.start()
    return server