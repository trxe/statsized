# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import statsized_pb2 as statsized__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in statsized_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class StatsizedStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetCurrentGames = channel.unary_unary(
                '/statsized.Statsized/GetCurrentGames',
                request_serializer=statsized__pb2.RequestFilter.SerializeToString,
                response_deserializer=statsized__pb2.Response.FromString,
                _registered_method=True)


class StatsizedServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetCurrentGames(self, request, context):
        """rpc StreamPlays (RequestFilter) returns (stream Play);
        rpc StreamShifts (RequestFilter) returns (stream Shift);
        rpc StreamScores (RequestFilter) returns (stream Score);
        rpc StreamClock (RequestFilter) returns (stream Clock);
        rpc GetPlays (Game) returns (Play);
        rpc GetShifts (Game) returns (Shift);
        rpc GetScores (Game) returns (Score);
        rpc GetClock (Game) returns (Clock);
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_StatsizedServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetCurrentGames': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCurrentGames,
                    request_deserializer=statsized__pb2.RequestFilter.FromString,
                    response_serializer=statsized__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'statsized.Statsized', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('statsized.Statsized', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Statsized(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetCurrentGames(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/statsized.Statsized/GetCurrentGames',
            statsized__pb2.RequestFilter.SerializeToString,
            statsized__pb2.Response.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
