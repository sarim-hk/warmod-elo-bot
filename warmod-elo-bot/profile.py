import queries

def run(c, steam_id):

    data = queries.stats_from_user_data_where_id(c, steam_id)
    games = get_total_games(data)

    print(f"{round(data[2]/games, 2)} kills per game")
    print(f"{round(data[3]/games, 2)} assists per game")
    print(f"{round(data[4]/games, 2)} deaths per game")
    print(f"{round(data[5]/games, 2)} 1v1s per game")
    print(f"{round(data[6]/games, 2)} 1v2s per game")
    print(f"{round(data[7]/games, 2)} 1v3s per game")
    print(f"{round(data[8]/games, 2)} headshots per game")

def get_total_games(data):
    return data[-1] + data[-2]

if __name__ == "__main__":
    import sqlite3
    conn = sqlite3.connect("elo.db")
    c = conn.cursor()
    run(c, "STEAM_1:0:158967782")
    print()
    run(c, "STEAM_1:0:115869435")
