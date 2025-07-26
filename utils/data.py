import os

from models.player import Player


def save_file(data: str, path: str):
    f = open(path, "w")
    f.write(data)
    f.close()


def dump_players(players: list[Player] | dict[str, Player]):
    if not os.path.exists("results/players/"):
        os.makedirs("results/players/")
    if not os.path.exists("results/teams/"):
        os.makedirs("results/teams/")
    if isinstance(players, list):
        for player in players:
            json_str = str(player.to_json())
            save_file(json_str, f"results/players/{player.uuid}.json")
    if isinstance(players, dict):
        for i in players.keys():
            player = players[i]
            json_str = str(player.to_json())
            save_file(json_str, f"results/players/{player.uuid}.json")
