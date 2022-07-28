import glob
import logging
import json
import os

def run(PATH=None):
    full_time = False
    playerstats = {}

    filename = get_oldest_unparsed_log(PATH)

    if not filename:
        return False, None

    loglines = open_log(filename)

    if force_end_check(loglines):
        mark_as_parsed(filename)
        logging.debug("Game was force ended.")
        return False, None

    if not log_ended_yet(loglines):
        logging.debug("Log not ended yet.")
        return False, None

    filesize = os.path.getsize(filename)
    if filesize < 400000:
        logging.debug("File size too small.")
        mark_as_parsed(filename)
        return False, None

    for index, line in enumerate(loglines):
        event = dictify_line(line)
        if not event:
            continue

        playerstats = parse_round_stats(playerstats, event)
        playerstats = parse_player_suicide(playerstats, event)
        playerstats = parse_clutches(playerstats, event)
        playerstats = parse_flashes(playerstats, index, loglines, event)
        playerstats = parse_player_hurt_util(playerstats, event)

        if not full_time:
            teamstats, full_time = parse_full_time(event)

    if full_time:
        if not teams_too_small_or_big(playerstats):
            mark_as_parsed(filename)
            return {"playerstats": playerstats, "teamstats": teamstats}, filename
        else:
            mark_as_parsed(filename)
            logging.debug("Teams too small or big.")
            print({"playerstats": playerstats, "teamstats": teamstats})
            return False, None
    else:
        mark_as_parsed(filename)
        logging.debug(f"Didn't go live or didn't reach full time: full_time = {full_time}")
        return False, None

def get_oldest_unparsed_log(PATH=None):
    if PATH is None:
        PATH = "/root/.steam/steamapps/common/Counter-Strike Global Offensive Beta - Dedicated Server/csgo/warmod/"
    PATH = f"{PATH}*.log"
    files = glob.glob(PATH)
    if not files:   # if empty
        return False

    files = sorted(files)
    filename = files[0]
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
        logging.error("Exception occurred, probably a player_say event")
        return False
    return event

def parse_player_hurt_util(playerstats, event):
    if event["event"] == "player_hurt":
        if event["weapon"] == "inferno":
            if event["attacker"]["uniqueId"] not in playerstats:
                playerstats[event["attacker"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "ef": 0, "ef_duration": 0, "he_ud": 0, "inferno_ud": 0, "team_id": None}
            playerstats[event["attacker"]["uniqueId"]]["inferno_ud"] += event["damage"]

        elif event["weapon"] == "hegrenade":
            if event["attacker"]["uniqueId"] not in playerstats:
                playerstats[event["attacker"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "ef": 0, "ef_duration": 0, "he_ud": 0, "inferno_ud": 0, "team_id": None}
            playerstats[event["attacker"]["uniqueId"]]["he_ud"] += event["damage"]
    return playerstats

def parse_flashes(playerstats, index, loglines, event):
    index_increment = 0
    if event["event"] == "grenade_detonate" and event["grenade"] == "flashbang":
        timestamp = event["timestamp"]
        thrower = event["player"]["uniqueId"]
        thrower_team = event["player"]["team"]
    else:
        return playerstats

    while True:
        index_increment += 1
        event = dictify_line(loglines[index+index_increment])
        try:
            if event["timestamp"] == timestamp:
                if event["event"] == "player_blind":
                    if thrower_team != event["player"]["team"]:
                        if thrower not in playerstats:
                            playerstats[thrower] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "ef": 0, "ef_duration": 0, "he_ud": 0, "inferno_ud": 0, "team_id": None}

                        playerstats[thrower]["ef"] += 1
                        playerstats[thrower]["ef_duration"] += event["duration"]
            else:
                break
        except Exception:
          print(event)

        else:
            break

    return playerstats

def parse_round_stats(playerstats, event):
    if event["event"] == "round_stats":
        if event["player"]["uniqueId"] not in playerstats:
            playerstats[event["player"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "ef": 0, "ef_duration": 0, "he_ud": 0, "inferno_ud": 0, "team_id": None}
            if event["player"]["team"] != 0:
                playerstats[event["player"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "ef": 0, "ef_duration": 0, "he_ud": 0, "inferno_ud": 0, "team_id": None}
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
            playerstats[event["player"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "ef": 0, "ef_duration": 0, "he_ud": 0, "inferno_ud": 0, "team_id": None}

        playerstats[event["player"]["uniqueId"]]["kills"] -= 1
        playerstats[event["player"]["uniqueId"]]["deaths"] += 1
    return playerstats

def parse_clutches(playerstats, event):
    if event["event"] == "player_clutch":
        if event["player"]["uniqueId"] not in playerstats:
            playerstats[event["attacker"]["uniqueId"]] = {"kills": 0, "deaths": 0, "assists": 0, "v1": 0, "v2": 0, "v3": 0, "headshots": 0, "ef": 0, "ef_duration": 0, "he_ud": 0, "inferno_ud": 0, "team_id": None}

        if event["won"] == 1:
            vs = event["versus"]
            try:
                playerstats[event["player"]["uniqueId"]][f"v{vs}"] += 1
            except KeyError:
                pass

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
    if len(playerstats) == 6:
        return False
    else:
        return True
