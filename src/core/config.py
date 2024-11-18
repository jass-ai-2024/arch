import os
from dotenv import load_dotenv

load_dotenv()


class Configs:
    DB_NAME: str = os.getenv("GPT_TOKEN")
