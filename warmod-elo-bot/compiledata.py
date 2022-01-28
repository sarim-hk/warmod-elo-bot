import queries

def run(gamestats, c, conn):
    # updating elo
    winner_team_id, loser_team_id = find_winning_team_id(gamestats)
    add_players_to_db_if_not_exist(gamestats, c, conn)
    teamelo = get_avg_team_elo(gamestats, c)
    win_percentage = get_win_chances(teamelo, winner_team_id, loser_team_id)
    net_elo_change = int(50 * (1-win_percentage))

    for player_id in gamestats["playerstats"]:
        if gamestats["playerstats"][player_id]["team_id"] == winner_team_id:
            queries.update_elo_wins_losses(net_elo_change, True, player_id, c)
        else:
            queries.update_elo_wins_losses(net_elo_change, False, player_id, c)
    conn.commit()

    # updating kda and clutches
    for player_id in gamestats["playerstats"]:
        kills, deaths, assists = gamestats["playerstats"][player_id]["kills"], gamestats["playerstats"][player_id]["deaths"], gamestats["playerstats"][player_id]["assists"]
        v1, v2, v3 = gamestats["playerstats"][player_id]["v1"], gamestats["playerstats"][player_id]["v2"], gamestats["playerstats"][player_id]["v3"]
        headshots = gamestats["playerstats"][player_id]["headshots"]
        queries.update_kda_clutches(kills, deaths, assists, v1, v2, v3, headshots, player_id, c, conn)


def find_winning_team_id(gamestats):
    if gamestats["teamstats"][list(gamestats["teamstats"])[0]] > gamestats["teamstats"][list(gamestats["teamstats"])[1]]:
        winner_team_id = list(gamestats["teamstats"])[0]
        loser_team_id = list(gamestats["teamstats"])[1]
    else:
        winner_team_id = list(gamestats["teamstats"])[1]
        loser_team_id = list(gamestats["teamstats"])[0]
    return winner_team_id, loser_team_id

def add_players_to_db_if_not_exist(gamestats, c, conn):
    for player_id in gamestats["playerstats"]:
        user_data = queries.elo_from_user_id(player_id, c)

        if user_data is None:
            queries.insert_default_values(player_id, c, conn)

def get_avg_team_elo(gamestats, c):
    teamelo = {}
    for player_id in gamestats["playerstats"]:
        if not gamestats["playerstats"][player_id]["team_id"] in teamelo:
            teamelo[gamestats["playerstats"][player_id]["team_id"]] = []

        player_elo = queries.elo_from_user_id(player_id, c)
        if player_elo is None:
            player_elo = 1000
        else:
            player_elo = player_elo[0]

        teamelo[gamestats["playerstats"][player_id]["team_id"]].append(player_elo)

    print(teamelo)
    for team_id in teamelo:
        teamelo[team_id] = sum(teamelo[team_id]) / len(teamelo[team_id])
    return teamelo

def get_win_chances(teamelo, winner_team_id, loser_team_id):
    win_percentage = 1 / (1 + 10 ** ((teamelo[loser_team_id] - teamelo[winner_team_id]) / 400))
    win_percentage = max(min(win_percentage, 0.99), 0.01)
    return win_percentage
