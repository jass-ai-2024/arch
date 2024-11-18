from openai import OpenAI
from .prompt import Prompts
from .config import Configs

prompts = Prompts()
configs = Configs()
openai_client = OpenAI(api_key=configs.GPT_TOKEN)
