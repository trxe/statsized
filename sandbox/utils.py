import datetime 
import pytz
import psycopg
import data_fetcher
import re

def compute_start_time_local(landing):
    startutc = datetime.datetime.fromisoformat(landing['startTimeUTC'].replace("Z", "+00:00"))
    venue_tz = pytz.timezone(landing['venueTimezone'])
    return startutc.astimezone(venue_tz)

# params = "/?game_id=2024200007&link=https%3A%2F%2Fapi-web.nhle.com%2Fv1%2Fgamecenter%2F2024200007%2Fplay-by-play&actions=teams&actions=players&actions=roster&actions=plays"
# parts = [x.split('=') for x in params.replace('?', '').split('&')]
# body = {}
# for param in parts:
#     if not body.get(param[0]):
#         body[param[0]] = []
#     body[param[0]].append(''.join(param[1:]))
# print(body)

# stime = compute_start_time_local({
#     'startTimeUTC': "2025-01-17T00:00:00Z",
#     'venueUTCOffset': "-05:00",
#     'venueTimezone': "US/Eastern"
# })
# game_id = 2024020885
# landing = data_fetcher.get_landing(game_id)
# print(stime.time() < datetime.time(18, 0)) 
# local_time = compute_start_time_local(landing)

# game_summary = {
#     'game': game_id,
#     'home_team': landing['homeTeam']['abbrev'],
#     'home_team_score': landing['homeTeam'].get('score', None),
#     'home_team_sog': landing['homeTeam'].get('sog', None),
#     'datetime': local_time,
#     'is_matinee': local_time.time() < datetime.time(18, 0),
#     'away_team': landing['awayTeam']['abbrev'],
#     'away_team_score': landing['awayTeam'].get('score', None),
#     'away_team_sog': landing['awayTeam'].get('sog', None),
#     'end_period': landing['periodDescriptor'].get('number'),
#     'end_period_type': landing['periodDescriptor'].get('periodType'),
# }

with psycopg.connect("dbname=nhl user=trxe") as conn:


    # Execute a command: this creates a new table
    gameres = conn.execute("""
        CREATE TABLE IF NOT EXISTS testing (
            info TEXT,
            number INT PRIMARY KEY
        );""")
    conn.commit()

    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no SQL injections!)
    values = [("23980", 1), ("hey", 1), ("bitch", 93)]
    # # args_str = ','.join(conn.mogrify("(%s, %s)", x) for x in test_inputs)
    # placeholders = ', '.join(['%s'] * len(values[0]))
    # # Wrap in parentheses.
    # values_clause =  f"""({placeholders})"""
    # # Inject into the query string.
    # isql = isql % values_clause

    # with conn.cursor() as cur:
    #     cur.executemany(isql, values)
    # conn.commit()
    args_str = "(%s, %s)"
    with conn.cursor() as cur:
        cur.executemany(
            f"""
            INSERT INTO testing ( info, number )
            VALUES {args_str}
            ON CONFLICT (number) 
            DO NOTHING 
            RETURNING info, number;
            """,values
            )
    conn.commit()

    # Query the database and obtain data as Python objects.
    selection = conn.execute("SELECT * FROM testing;")
    resp = selection.fetchall()
    # will return (1, 100, "abc'def")

    # You can use `conn.fetchmany()`, `cur.fetchall()` to return a list
    # of several records, or even iterate on the connsor
    print("records:")
    for record in resp:
        print(record)

    # Make the changes to the database persistent