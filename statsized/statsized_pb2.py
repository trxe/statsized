# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: statsized.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'statsized.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fstatsized.proto\x12\tstatsized\"\x1e\n\x06\x43oords\x12\t\n\x01x\x18\x01 \x01(\x01\x12\t\n\x01y\x18\x02 \x01(\x01\"\x14\n\x06Player\x12\n\n\x02id\x18\x01 \x01(\x03\"\x12\n\x04Team\x12\n\n\x02id\x18\x01 \x01(\x03\"\xb8\x03\n\x04Game\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x13\n\x06season\x18\x02 \x01(\x05H\x00\x88\x01\x01\x12\x19\n\x0cgame_type_id\x18\x03 \x01(\x05H\x01\x88\x01\x01\x12\x1b\n\x0estart_time_utc\x18\x04 \x01(\tH\x02\x88\x01\x01\x12\x1d\n\x10venue_utc_offset\x18\x05 \x01(\tH\x03\x88\x01\x01\x12\x1b\n\x0evenue_timezone\x18\x06 \x01(\tH\x04\x88\x01\x01\x12\x17\n\ngame_state\x18\x07 \x01(\tH\x05\x88\x01\x01\x12\'\n\thome_team\x18\x08 \x01(\x0b\x32\x0f.statsized.TeamH\x06\x88\x01\x01\x12\'\n\taway_team\x18\t \x01(\x0b\x32\x0f.statsized.TeamH\x07\x88\x01\x01\x12\x1b\n\x0egamecenter_url\x18\n \x01(\tH\x08\x88\x01\x01\x42\t\n\x07_seasonB\x0f\n\r_game_type_idB\x11\n\x0f_start_time_utcB\x13\n\x11_venue_utc_offsetB\x11\n\x0f_venue_timezoneB\r\n\x0b_game_stateB\x0c\n\n_home_teamB\x0c\n\n_away_teamB\x11\n\x0f_gamecenter_url\"\x87\x01\n\x06\x46ilter\x12\x1d\n\x04game\x18\x01 \x01(\x0b\x32\x0f.statsized.Game\x12\"\n\x04team\x18\x02 \x01(\x0b\x32\x0f.statsized.TeamH\x00\x88\x01\x01\x12&\n\x06player\x18\x03 \x01(\x0b\x32\x11.statsized.PlayerH\x01\x88\x01\x01\x42\x07\n\x05_teamB\t\n\x07_player\"P\n\rRequestFilter\x12\x0c\n\x04host\x18\x01 \x01(\t\x12&\n\x06\x66ilter\x18\x02 \x01(\x0b\x32\x11.statsized.FilterH\x00\x88\x01\x01\x42\t\n\x07_filter\"*\n\x08Response\x12\x1e\n\x05games\x18\x01 \x03(\x0b\x32\x0f.statsized.Game\"L\n\x05\x43lock\x12\x19\n\x11seconds_remaining\x18\x01 \x01(\x05\x12\x0f\n\x07running\x18\x02 \x01(\x08\x12\x17\n\x0fin_intermission\x18\x03 \x01(\x08\"\x97\x01\n\x0ePlayerKeyFrame\x12\n\n\x02id\x18\x01 \x01(\x03\x12!\n\x06player\x18\x02 \x01(\x0b\x32\x11.statsized.Player\x12\x15\n\rjersey_number\x18\x03 \x01(\x03\x12\x1d\n\x04team\x18\x04 \x01(\x0b\x32\x0f.statsized.Team\x12 \n\x05\x63oord\x18\x05 \x01(\x0b\x32\x11.statsized.Coords\"\'\n\tAttribute\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"\xbe\x01\n\x05Shift\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x13\n\x0b\x64\x65tail_code\x18\x02 \x01(\x05\x12\x10\n\x08start_ts\x18\x03 \x01(\x03\x12\x0e\n\x06\x65nd_ts\x18\x04 \x01(\x03\x12!\n\x06player\x18\x05 \x01(\x0b\x32\x11.statsized.Player\x12\x1d\n\x04team\x18\x06 \x01(\x0b\x32\x0f.statsized.Team\x12\x11\n\tshift_num\x18\x07 \x01(\x03\x12\x1d\n\x04game\x18\x08 \x01(\x0b\x32\x0f.statsized.Game\"\xa4\x02\n\x0bPlayerEvent\x12\n\n\x02id\x18\x01 \x01(\x03\x12!\n\x06player\x18\x02 \x01(\x0b\x32\x11.statsized.Player\x12\x12\n\nevent_code\x18\x03 \x01(\x03\x12\r\n\x05\x65vent\x18\x04 \x01(\t\x12\x17\n\nevent_role\x18\x06 \x01(\tH\x00\x88\x01\x01\x12.\n\x10\x65vent_owner_team\x18\x07 \x01(\x0b\x32\x0f.statsized.TeamH\x01\x88\x01\x01\x12#\n\x05\x61ttrs\x18\x08 \x03(\x0b\x32\x14.statsized.Attribute\x12&\n\x06\x63oords\x18\t \x01(\x0b\x32\x11.statsized.CoordsH\x02\x88\x01\x01\x42\r\n\x0b_event_roleB\x13\n\x11_event_owner_teamB\t\n\x07_coords\"\xdf\x01\n\x04Play\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0e\n\x06period\x18\x02 \x01(\x05\x12\x18\n\x10time_since_start\x18\x03 \x01(\x05\x12\x16\n\x0esituation_code\x18\x04 \x01(\t\x12 \n\x18home_team_defending_side\x18\x05 \x01(\t\x12\x11\n\ttype_code\x18\x06 \x01(\x05\x12\x11\n\ttype_desc\x18\x07 \x01(\t\x12\x12\n\nsort_order\x18\x08 \x01(\x05\x12-\n\rplayer_events\x18\t \x03(\x0b\x32\x16.statsized.PlayerEvent\"\xb3\x01\n\x05Score\x12\x16\n\x0esituation_code\x18\x01 \x01(\t\x12\x12\n\nevent_code\x18\x02 \x01(\x05\x12!\n\x06player\x18\x03 \x01(\x0b\x32\x11.statsized.Player\x12\"\n\x07\x61ssists\x18\x04 \x03(\x0b\x32\x11.statsized.Player\x12\x0f\n\x07is_home\x18\x05 \x01(\x08\x12\x12\n\nhome_score\x18\x06 \x01(\x05\x12\x12\n\naway_score\x18\x07 \x01(\x05\x32M\n\tStatsized\x12@\n\x0fGetCurrentGames\x12\x18.statsized.RequestFilter\x1a\x13.statsized.Responseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'statsized_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_COORDS']._serialized_start=30
  _globals['_COORDS']._serialized_end=60
  _globals['_PLAYER']._serialized_start=62
  _globals['_PLAYER']._serialized_end=82
  _globals['_TEAM']._serialized_start=84
  _globals['_TEAM']._serialized_end=102
  _globals['_GAME']._serialized_start=105
  _globals['_GAME']._serialized_end=545
  _globals['_FILTER']._serialized_start=548
  _globals['_FILTER']._serialized_end=683
  _globals['_REQUESTFILTER']._serialized_start=685
  _globals['_REQUESTFILTER']._serialized_end=765
  _globals['_RESPONSE']._serialized_start=767
  _globals['_RESPONSE']._serialized_end=809
  _globals['_CLOCK']._serialized_start=811
  _globals['_CLOCK']._serialized_end=887
  _globals['_PLAYERKEYFRAME']._serialized_start=890
  _globals['_PLAYERKEYFRAME']._serialized_end=1041
  _globals['_ATTRIBUTE']._serialized_start=1043
  _globals['_ATTRIBUTE']._serialized_end=1082
  _globals['_SHIFT']._serialized_start=1085
  _globals['_SHIFT']._serialized_end=1275
  _globals['_PLAYEREVENT']._serialized_start=1278
  _globals['_PLAYEREVENT']._serialized_end=1570
  _globals['_PLAY']._serialized_start=1573
  _globals['_PLAY']._serialized_end=1796
  _globals['_SCORE']._serialized_start=1799
  _globals['_SCORE']._serialized_end=1978
  _globals['_STATSIZED']._serialized_start=1980
  _globals['_STATSIZED']._serialized_end=2057
# @@protoc_insertion_point(module_scope)
