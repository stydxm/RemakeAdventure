import json
import uuid


class Team:
    chat_history: list[dict[str, str | int]] = []
    summary: str

    def __init__(self, members: list[str], team_uuid: str = ""):
        if team_uuid == "":
            self.uuid = str(uuid.uuid4())
        else:
            self.uuid = team_uuid
        self.members = members

    def to_json(self):
        members = []
        for member in self.members:
            members.append(member)
        return json.dumps({
            "members": members,
            "uuid": self.uuid,
            "chat_history": self.chat_history,
            "summary": self.summary
        }, ensure_ascii=False)


def recover_team(data: dict) -> Team:
    return Team(members=data["members"], team_uuid=data["uuid"])
