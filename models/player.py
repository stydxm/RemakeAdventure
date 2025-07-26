import json
import random
import uuid
from typing import Literal, Union, get_args

from models import team
from utils import llm

Developer = Literal["developer"]
Designer = Literal["designer"]
Hacker = Literal["hacker"]
Role = Union[Developer, Designer, Hacker]


class Player:
    team_id: team.Team
    chat_history: list[dict[Literal["role", "content"], str | int]]

    def __init__(self, temperature: float, role: Role, player_uuid: str = "", introduction: str = ""):
        if player_uuid == "":
            self.uuid = str(uuid.uuid4())
        else:
            self.uuid = player_uuid
        self.temperature = temperature
        self.model = llm.kimi_client, "kimi-k2-0711-preview"
        self.role = role
        if introduction == "":
            self.init_chat_history()
        else:
            self.introduction = introduction

    def init_chat_history(self):
        fe = random.choice([True, False])
        be = random.choice([True, False])
        ai = random.choice([True, False])
        ability = random.choice(["优秀", "普通", "略低于同行"])
        initial_prompts: dict[any, str] = {
            Developer: f"你是一位能力{ability}的软件工程师，擅长{'前端、' if fe else ''}{'后端、' if be else ''}{'AI调用' if ai else ''}等开发技能。",
            Designer: f"你是一位能力{ability}的设计师，擅长UI/UX设计。",
            Hacker: "你是一个嬉皮士，擅长亲手创造出各种有意思的东西。"
        }
        initial_prompt = (initial_prompts[self.role] +
                          "现在你正在参加一场全中国最大的黑客松，要与在几天的时间里与队友一起，"
                          "按主办方准备的主题创造出一些有创意的内容。请不要过度描述细节，尤其是过于详细的数字。")
        initial_prompt += "你的姓不是“林”“李”或者“王”。" if random.random() < 0.9 else ""
        self.chat_history = [{"role": "system", "content": initial_prompt}]

    def chat(self, message: str):
        if self.chat_history is None:
            self.init_chat_history()
        self.chat_history.append({"role": "user", "content": message})
        response = self.model[0].chat.completions.create(
            model=self.model[1],
            temperature=self.temperature,
            messages=self.chat_history
        )
        # self.chat_history.append({
        #     "role": "assistant",
        #     "content": str(response.choices[0].message.content)
        # })
        return response

    def to_json(self):
        result = {
            "uuid": self.uuid,
            "temperature": round(self.temperature, 2),
            "role": get_args(self.role)[0],
            "introduction": str(self.chat_history[-1]["content"]),
        }
        return json.dumps(result, ensure_ascii=False)


def recover_player(data: dict) -> Player:
    return Player(
        player_uuid=data["uuid"],
        temperature=data["temperature"],
        role=data["role"],
        introduction=data["introduction"]
    )
