import os

from openai import OpenAI

kimi_client = OpenAI(api_key=os.environ.get("KIMI_API_KEY"), base_url="https://api.moonshot.cn/v1")
