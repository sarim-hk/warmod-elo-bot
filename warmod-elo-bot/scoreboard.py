from tabulate import tabulate
import topelo as te
import compiledata as cd
import queries
import pprint

def run(gamestats, filename, c, steamkey):

    winner_team_id, loser_team_id = cd.find_winning_team_id(gamestats)

    pprint.pprint(gamestats)
    print(winner_team_id, loser_team_id)

    teamelo = cd.get_avg_team_elo(gamestats, c)
    print(teamelo)
    win_percentage = cd.get_win_chances(teamelo, winner_team_id, loser_team_id)
    print(win_percentage)
    net_elo_change = int(50 * (1-win_percentage))
    print(net_elo_change)

    steamids = list(gamestats["playerstats"])
    for steamid in steamids:
        steamid64 = te.steamid_to_64bit(steamid)
        username = {"username": te.id64_to_username(steamid64, steamkey)}
        gamestats["playerstats"][steamid] = {**username, **gamestats["playerstats"][steamid]}

    scoreboard = {"team2": [], "team3": []}
    for player in gamestats["playerstats"]:
        team_id = gamestats["playerstats"][player]["team_id"]
        gamestats["playerstats"][player]["Score"] = None
        scoreboard[f"team{team_id}"].append(list(gamestats["playerstats"][player].values()))

    pages = []
    for team in scoreboard:
        team_id = int(team[4])

        score = gamestats["teamstats"][team_id]
        if team_id == winner_team_id:
            page = tabulate((team[:8]+team[9:] for team in scoreboard[team]),
            headers=["Name", "Kills", "Deaths", "Assists", "1v1", "1v2", "1v3", "Headshots", f"Score: {score}  ELO: +{net_elo_change}"])
        else:
            page = tabulate((team[:8]+team[9:] for team in scoreboard[team]),
            headers=["Name", "Kills", "Deaths", "Assists", "1v1", "1v2", "1v3", "Headshots", f"Score: {score}  ELO: -{net_elo_change}"])

        date = filename_to_date(filename)
        pages.append(page)
    pages = "\n\n".join(pages)
    pages = f"```glsl\n{date}\n\n{pages}```"

    """
    f = open("test.txt", "a")
    f.write(f"{teamelo[winner_team_id]}, {teamelo[loser_team_id]}\n")
    f.write(f"{win_percentage}\n")
    f.write(f"{net_elo_change}\n")
    f.write("\n")
    f.write(pages)
    f.write("\n\n\n")
    f.close()
    """

    return pages

def filename_to_date(filename):
    index = filename.find("warmod/") + 7
    filename = filename[index:]
    filename = filename.split("-")[:4]
    filename[3] = f"{filename[3][:2]}:{filename[3][2:]}"

    date = f"{filename[2]}/{filename[1]}/{filename[0]} {filename[3]}"
    return date
