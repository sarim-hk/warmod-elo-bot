import glob
import logging
import json
import os

def run(PATH=None):
    live_on_3 = False
    full_time = False
    playerstats = {}

    filename = get_oldest_unparsed_log(PATH)

    if not filename:
        return False

    loglines = open_log(filename)

    if not log_ended_yet(loglines):
        logging.debug("Log not ended yet.")
        return False

    if force_end_check(loglines):
        mark_as_parsed(filename)
        logging.debug("Game was force ended.")
        return False

    for index, line in enumerate(loglines):
        event = dictify_line(line)

        if not live_on_3:
            live_on_3 = parse_live_on_3(event)

        elif live_on_3:
            playerstats = parse_round_stats(playerstats, event)
            playerstats = parse_player_suicide(playerstats, event)
            playerstats = parse_clutches(playerstats, event)

            if not full_time:
                teamstats, full_time = parse_full_time(event)
            else:
                if not teams_too_small_or_big(playerstats):
                    mark_as_parsed(filename)
                    return {"playerstats": playerstats, "teamstats": teamstats}
                else:
                    mark_as_parsed(filename)
                    logging.debug("Teams too small or big.")
                    return False

    mark_as_parsed(filename)
    logging.debug(f"Didn't go live or didn't reach full time: full_time = {full_time}, live_on_3 = {live_on_3}")
    return False

def get_oldest_unparsed_log(PATH=None):
    if PATH is None:
        PATH = "/root/.steam/steamapps/common/Counter-Strike Global Offensive Beta - Dedicated Server/csgo/warmod/"
    PATH = f"{PATH}*.log"
    files = glob.glob(PATH)
    if not files:   # if empty
        return False

    filename = min(files, key=os.path.getmtime)
    logging.debug(filename)
    return filename

def open_log(filename):
    with open(filename, encoding='utf-8') as f:
        lines = f.readlines()
    return lines

def log_ended_yet(loglines):
    try:
        event = json.loads(loglines[-1])
        if event["event"] == "log_end":
            return True
        return False
    except Exception:
        logging.error("Exception occurred", exc_info=True)
        return False

def mark_as_parsed(filename):
    os.rename(filename, filename+"parsed")

def force_end_check(loglines):
    try:
        event = json.loads(loglines[-1])
        if event["event"] == "force_end":
            return True
        return False
    except Exception:
        logging.error("Exception occurred:", exc_info=True)
        return False

def dictify_line(line):
    try:
        event = json.loads(line)
    except Exception as e:
        logging.error("Exception occurred, probably a player_say event:", exc_info=True)
    return event

def parse_live_on_3(event):
    if event["event"] == "live_on_3":
        return True

def parse_round_stats(playerstats, event):
    if event["event"] == "round_stats":
        if event["player"]["uniqueId"] not in playerstats:
            if event["player"]["team"] != 0:
                playerstats[event["player"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "team_id": None}
            # disconnect before half time maybe

        playerstats[event["player"]["uniqueId"]]["kills"] += event["kills"]
        playerstats[event["player"]["uniqueId"]]["assists"] += event["assists"]
        playerstats[event["player"]["uniqueId"]]["deaths"] += event["deaths"]
        playerstats[event["player"]["uniqueId"]]["headshots"] += event["headshots"]
        playerstats[event["player"]["uniqueId"]]["team_id"] = event["player"]["team"]
    return playerstats

def parse_player_suicide(playerstats, event):
    if event["event"] == "player_suicide":
        if event["player"]["uniqueId"] not in playerstats:
            playerstats[event["player"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "team_id": None}

        playerstats[event["player"]["uniqueId"]]["kills"] -= 1
        playerstats[event["player"]["uniqueId"]]["deaths"] += 1
    return playerstats

def parse_clutches(playerstats, event):
    vs = 0
    if event["event"] == "player_clutch":
        if event["player"]["uniqueId"] not in playerstats:
            playerstats[event["attacker"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "team_id": None}

        if event["won"] == 1:
            vs = event["versus"]
            playerstats[event["player"]["uniqueId"]][f"v{vs}"] += 1
    return playerstats

def parse_full_time(event):
    if event["event"] == "full_time" or event["event"] == "over_full_time":
        teamstats = {event["teams"][0]["team"]: event["teams"][0]["score"],
                    event["teams"][1]["team"]: event["teams"][1]["score"]}
        full_time = True
    else:
        teamstats = None
        full_time = False
    return teamstats, full_time

def teams_too_small_or_big(playerstats):
    logging.debug(playerstats.keys())
    if len(playerstats) == 6:
        return False
    else:
        return True
