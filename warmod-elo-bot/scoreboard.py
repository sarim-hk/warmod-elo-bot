from tabulate import tabulate
import topelo as te
import pprint
def run(gamestats, steamkey):

    steamids = list(gamestats["playerstats"])
    for steamid in steamids:
        gamestats["playerstats"][steamid]["None"] = None
        steamid64 = te.steamid_to_64bit(steamid)
        username = {"username": te.id64_to_username(steamid64, steamkey)}
        gamestats["playerstats"][steamid] = {**username, **gamestats["playerstats"][steamid]}

    scoreboard = {"team2": [], "team3": []}
    for player in gamestats["playerstats"]:
        team_id = gamestats["playerstats"][player]["team_id"]
        scoreboard[f"team{team_id}"].append(list(gamestats["playerstats"][player].values()))

    pages = []
    for team in scoreboard:
        score = gamestats["teamstats"][int(team[4])]
        page = tabulate((team[:8]+team[9:] for team in scoreboard[team]), headers=["Name", "Kills", "Deaths", "Assists", "1v1", "1v2", "1v3", "Headshots", f"Score: {score}"])
        page = f"```glsl\n{page}```"
        pages.append(page)
    return pages
