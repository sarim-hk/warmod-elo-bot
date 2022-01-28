def create_table(c, conn):
    sql_query = """
    CREATE TABLE IF NOT EXISTS user_data (
    USER_ID         TEXT    (0, 50),
    ELO             INTEGER (0, 20),
    KILLS           INTEGER (0, 20),
    DEATHS          INTEGER (0, 20),
    ASSISTS         INTEGER (0, 20),
    v1              INTEGER (0, 20),
    v2              INTEGER (0, 20),
    v3              INTEGER (0, 20),
    HEADSHOTS       INTEGER (0, 20),
    WIN             INTEGER (0, 20),
    LOSS            INTEGER (0, 20)
    );"""
    c.execute(sql_query)
    conn.commit()

def elo_from_user_id(player_id, c):
    sql_query = f'SELECT ELO FROM user_data WHERE USER_ID = ?'
    user_data = c.execute(sql_query, (player_id,)).fetchone()
    return user_data

def insert_default_values(player_id, c, conn):
    sql_query = "INSERT OR REPLACE INTO user_data (USER_ID, ELO, KILLS, DEATHS, ASSISTS, v1, v2, v3, HEADSHOTS, WIN, LOSS) VALUES (?, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0);"
    c.execute(sql_query, (player_id,))
    conn.commit()

def update_elo_wins_losses(net_elo_change, win, player_id, c):
    if win:
        sql_query = f"""
                    UPDATE user_data
                    SET ELO = ELO + ?,
                        WIN = WIN + 1
                    WHERE USER_ID = ?
                    """
    else:
        sql_query = f"""
                    UPDATE user_data
                    SET ELO = ELO - ?,
                        LOSS = LOSS + 1
                    WHERE USER_ID = ?
                    """
    c.execute(sql_query, (net_elo_change, player_id))

def update_kda_clutches(kills, assists, deaths, v1, v2, v3, headshots, player_id, c, conn):
    sql_query = f"""UPDATE user_data
                SET KILLS = KILLS + ?,
                DEATHS = DEATHS + ?,
                ASSISTS = ASSISTS + ?,
                v1 = v1 + ?,
                v2 = v2 + ?,
                v3 = v3 + ?,
                HEADSHOTS = HEADSHOTS + ?
                WHERE USER_ID = ?
                """
    c.execute(sql_query, (kills, deaths, assists, v1, v2, v3, headshots, player_id))
    conn.commit()

def stats_from_user_data(c):
    sql_query = "SELECT * FROM user_data"
    c.execute(sql_query)
    user_data = c.execute(sql_query).fetchall()
    return user_data

def ids_from_user_data(c):
    sql_query = "SELECT USER_ID FROM user_data"
    c.execute(sql_query)
    user_data = c.execute(sql_query).fetchall()
    return user_data

def stats_from_user_data_where_id(c, player_id):
    sql_query = "SELECT * FROM user_data WHERE USER_ID = ?"
    user_data = c.execute(sql_query, (player_id,)).fetchone()
    return user_data
