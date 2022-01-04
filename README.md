
# [CS:GO] Warmod Stats Bot 

Warmod Stats Bot is an elo and leaderboard system written in Python. It reads [Warmod](https://forums.alliedmods.net/showthread.php?t=225474) .log files, processes the data and stores it in a database, accessible through Discord.

* ELO system
* Functional, well formatted leaderboards
* Tracks all relevant stats (KDA, HS%, Clutches, WL%)
* Low system requirements
## Installation

Must be run on the same machine as the CS:GO server. 

```bash
  pip install tabulate
  pip install discord
  python3 main.py

```

A `keys.txt` file must also be created in `warmod-elo-bot`, formatted as such:

```
DISCORDBOTTOKEN: descriptor
STEAMAPIKEY: descriptor
```
## Screenshots

![App Screenshot](https://i.imgur.com/1uq2Oqp.png)


## FAQ

#### My games are always listed as having too many or too little players, why?
This system is designed to work with 3v3 matches (6 players), so typical 5v5 matches won't initially work.  
You'll also face this issue if a player is swapped out mid-game.  
However the code can be easily modified to suit your needs in `parselogfiles.py > teams_too_small_or_big()`

#### My games simply aren't registering at all, why?
You either don't have Warmod logs set up, or you aren't starting your games correctly.  
A server admin should use `!fs` or everyone must `!ready` for the log to be generated.

Alternatively, you haven't set the correct log path. You can do this in `main.py > data_parser() > parselogfiles.run(PATH="PATH_HERE")`

#### Why aren't 1v4s or 1v5s tracked?
As aforementioned, the system is designed for 3v3 matches, where 1v4s/1v5s are impossible.  
However, the code can again be modified by:  
* Adding `2` to the variable `vs` in `parselogfiles.py > parse_clutches(playerstats, event)`
* Modifying the table headers in `topelo.py > run(steamkey, c)`
* This will change it from tracking `1v1, 1v2, 1v3` to `1v3, 1v4, 1v5`
