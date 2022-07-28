import urllib.request
import json
import queries
import re
from tabulate import tabulate

def run(steamkey, c):
    final = []
    user_data = queries.stats_from_user_data(c)
    user_data.sort(key=lambda y: y[1], reverse=True)


    for user_index, user in enumerate(user_data):
        user = list(user)
        steamid64 = steamid_to_64bit(user[0])
        username = id64_to_username(steamid64, steamkey)
        user[0] = remove_emoji(username)

        user = calculate_kd(user)
        user = calculate_win_loss(user)
        user = calculate_hs(user)
        user = calculate_ud_per_game(user)
        user = calculate_ef_per_game(user)
        user = calculate_ef_time_per_game(user)

        final.append(user)

    table = tabulate(final, headers=["Name", "ELO", "Kills", "Assists", "Death", "K/D", "HS", "1v1", "1v2", "1v3", "AVG EF", "AVG EF Time", "AVG UD", "Wins", "Losses", "W/L"])
    pages = re.compile("(?:^.*$\n?){1,12}",re.M).findall(table)
    pages = [f"```glsl\n{page}```" for page in pages]
    return pages

def steamid_to_64bit(steamid):
    steam64id = 76561197960265728
    id_split = steamid.split(":")
    steam64id += int(id_split[2]) * 2
    if id_split[1] == "1":
        steam64id += 1
    return steam64id

def bit64_to_steamid(steamid):
    y = int(steamid) - 76561197960265728
    x = y % 2
    return "STEAM_1:{}:{}".format(x, (y - x) // 2)

def id64_to_username(steamid64, steamkey):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steamkey}&steamids={steamid64}"
    with urllib.request.urlopen(url) as url:
        data = json.load(url)   # loaded as dict
    username = data["response"]["players"][0]["personaname"]
    return username

def id64s_to_username(steamid64, steamkey):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steamkey}&steamids={steamid64}"
    with urllib.request.urlopen(url) as url:
        data = json.load(url)   # loaded as dict
    users = data["response"]["players"]
    lower_usernames = [user["personaname"] for user in users]
    usernames = [user["personaname"].lower() for user in users]
    ids = [user["steamid"] for user in users]
    return lower_usernames, usernames, ids

def remove_emoji(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def calculate_kd(user):
    if user[2] == 0:
        user.insert(5, 0)
    elif user[4] == 0:
        user.insert(5, user[2])
    else:
        user.insert(5, round((user[2] / user[4]), 2))
    return user

def calculate_win_loss(user):
    if user[10] == 0:
        user.append("0%")
    elif user[11] == 0:
        user.append("100%")
    else:
        user.append(str(round((user[14] / (user[14] + user[15])) * 100, 2)) + "%")
    return user

def calculate_hs(user):
    headshots = int(user[9])
    user.pop(9)
    user.insert(6, str(round(((headshots / user[2]) * 100), 2)) + "%")
    return user

def calculate_ud_per_game(user):
    user[12] = user[12] + user[13]
    user.pop(13)

    games = user[13] + user[14]
    user[12] = round(user[12]/games)

    return user

def calculate_ef_per_game(user):
    games = user[13] + user[14]
    user[10] = round(user[10]/games)

    return user

def calculate_ef_time_per_game(user):
    games = user[13] + user[14]
    user[11] = round(user[11]/games)

    return user
