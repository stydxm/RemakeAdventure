import json
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from tqdm import tqdm

if os.environ.get("KIMI_API_KEY") is None:
    load_dotenv()
from utils import llm
from models import player, team

themes: list[str] = json.load(open("assets/themes.json"))
players: dict[str, player.Player] = {}
teams: list[team.Team] = []
model = llm.kimi_client
for player_files in os.listdir("results/players"):
    current_player = json.load(open("results/players/" + player_files))
    current_player = player.recover_player(current_player)
    players[current_player.uuid] = current_player
for team_files in os.listdir("results/teams"):
    current_team = json.load(open("results/teams/" + team_files))
    current_team = team.recover_team(current_team)
    teams.append(current_team)


def communicate(single_team: team.Team):
    end = False
    while not end:
        random.shuffle(single_team.members)
        for team_member in single_team.members:
            team_member_instance = players[team_member]
            member_introductions = "以下是你的队友："
            for other_member in single_team.members:
                if other_member != team_member:
                    member_introductions += players[other_member].introduction
            member_introductions += ""
            team_member_instance.chat_history = [
                {"role": "system",
                 "content": "现在你正在参加一场全中国最大的黑客松，要与在几天的时间里与队友一起创造出一些有意思的内容"},
                {"role": "system", "content": "主办方的赛道主题是：" + random.choice(themes)},
                {"role": "system", "content": "你的人设是：" + team_member_instance.introduction},
                {"role": "system", "content": member_introductions}
            ]
            for message in single_team.chat_history:
                team_member_instance.chat_history.append({"role": "user", "content": "你的队友说" + message["content"]})
            if len(single_team.chat_history) == 0:
                chat_prompt = "下面请你根据大家的能力和背景提出项目的想法，内容不要过于中二，并且尊重客观事实："
            else:
                chat_prompt = "下面请你发言，你可以赞同或者反对他人意见："
            if len(single_team.chat_history) >= len(single_team.members):
                chat_prompt += "如果你觉得讨论很成熟了，可以回答“结束”以停止讨论"
            response = team_member_instance.chat(chat_prompt)
            response_message = response.choices[0].message.content
            single_team.chat_history.append({
                "member": team_member_instance.uuid,
                "token": response.usage.completion_tokens,
                "content": response_message
            })
            if response_message.endswith("结束") or "结束" in response_message and len(response_message) < 50:
                end = True
                break
    summary_messages = [{"role": "system",
                         "content": "现在你正在参加一场全中国最大的黑客松，以下是你和队友们讨论的结果。请你简要总结并描述你们组想做的项目内容，不需要过度描述细节"}]
    chat_history_content = "讨论内容："
    for single_message in single_team.chat_history:
        chat_history_content += "另一位队友说：" + single_message["content"]
    summary_messages.append({"role": "user", "content": chat_history_content})
    response = model.chat.completions.create(
        model="kimi-k2-0711-preview",
        messages=summary_messages
    )
    single_team.summary = response.choices[0].message.content
    code_messages = [
        {"role": "system",
         "content": "现在你正在参加一场全中国最大的黑客松，现在你们已经完成了讨论，请你根据队友的能力，输出最后的内容。"
                    "如果队里有程序员，就输出最后的项目代码（不包含其他内容），否则输出一份项目计划书"},
        {"role": "system", "content": "你们的项目内容是：\n" + single_team.summary}
    ]
    member_introductions = "以下是你的队友："
    for other_member in single_team.members:
        member_introductions += "\n" + players[other_member].introduction
    code_messages.append({"role": "user", "content": member_introductions})
    response = model.chat.completions.create(
        model="kimi-k2-0711-preview",
        messages=code_messages
    )
    single_team.output = response.choices[0].message.content
    f = open(f"results/teams/{single_team.uuid}.json", "w")
    f.write(single_team.to_json())
    f.close()


progress_bar = tqdm(total=len(teams))
finished = 0
pool = ThreadPoolExecutor(max_workers=10)
futures = {pool.submit(communicate, i): i for i in teams}
for fut in as_completed(futures):
    idx = futures[fut]
    try:
        fut.result()
    except Exception as e:
        raise e
    finally:
        progress_bar.update(1)
progress_bar.close()
