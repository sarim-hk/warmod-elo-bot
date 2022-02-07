import queries

def run(c, steam_id):
    data = stats_from_user_data_where_id(c, steam_id)
    print(data)
