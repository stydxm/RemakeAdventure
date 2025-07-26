import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from tqdm import tqdm

if os.environ.get("KIMI_API_KEY") is None:
    load_dotenv()
from models import player, team
from utils import utils, data

temperature_samples = utils.truncated_normal(mean=0.8, std=0.4, size=100, lower_limit=0, upper_limit=0.8)
players: dict[str, player.Player] = {}


def create_player():
    role = random.choice([player.Developer, player.Developer, player.Developer, player.Designer, player.Hacker])
    test_player = player.Player(temperature=random.choice(temperature_samples), role=role)
    test_player.chat("你好，用几句话简单介绍一下你自己，并结合自己的人物设定写一些背景经历，但要尊重客观事实")
    players[test_player.uuid] = test_player


player_count = 10
progress_bar = tqdm(total=player_count)
finished = 0
pool = ThreadPoolExecutor(max_workers=10)
futures = {pool.submit(create_player): i for i in range(player_count)}
for fut in as_completed(futures):
    idx = futures[fut]
    try:
        fut.result()
    except Exception as e:
        raise e
    finally:
        progress_bar.update(1)
progress_bar.close()
data.dump_players(players)
last_player_index = 0
while len(players) - last_player_index > 1:
    members = []
    remaining_player_count = len(players) - last_player_index - 1
    if remaining_player_count >= 6:
        member_count = random.choice([2, 3, 4])
    elif remaining_player_count == 5 or remaining_player_count == 4:
        member_count = 2
    else:
        member_count = remaining_player_count
    player_uuids = tuple(players.keys())
    for i in player_uuids[last_player_index:last_player_index + member_count]:
        members.append(players[i].uuid)
    new_team = team.Team(members)
    f = open(f"results/teams/{new_team.uuid}.json", "w")
    f.write(new_team.to_json())
    f.close()
    last_player_index += member_count
