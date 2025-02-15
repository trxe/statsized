import math


class Parser:
    @classmethod
    def name(raw, name_field, subfield="default"):
        return raw.get(name_field).get(subfield, raw.get(name_field))

    @classmethod
    def player(cls, raw):
        return {
            "id": int(f"1{(raw.get('playerId'),)}"),
            "first_name": raw.name("firstName"),
            "last_name": raw.name("lastName"),
            "team": {"short": cls.name(raw, "teamAbbrev")},
        }

    @classmethod
    def team(cls, raw):
        return {
            "id": raw.get("id"),
            "name": raw.name("name"),
            "short": raw.get("abbrev"),
            "logo": raw.get("logo"),
            "logo_black": raw.get("logoBlack"),
        }

    @classmethod
    def game(cls, raw):
        return {
            "id": raw.get("id"),
            "season": math.floor(raw.get("id") / 10000),
            "game_type": raw.get("gameType"),
            "venue": raw.get("venue").get("default"),
            "start_time_utc": raw.get("startTimeUTC"),
            "venue_utc_offset": raw.get("venueUTCOffset"),
            "venue_timezone": raw.get("venueTimezone"),
            "game_state": raw.get("gameState"),
            "away_team": cls.team(raw.get("awayTeam")),
            "home_team": cls.team(raw.get("homeTeam")),
            "gamecenter_url": raw.get("gameCenterLink"),
        }

    @classmethod
    def score(cls, raw):
        return {
            "situation_code": raw.get("situationCode"),
            "eventId": raw.get("eventId"),
            "player": cls.player(raw),
        }
