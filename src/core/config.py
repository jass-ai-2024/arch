import os
from dotenv import load_dotenv

load_dotenv()


class Configs:
    GPT_TOKEN: str = os.getenv("GPT_TOKEN")
