from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from swarm import Swarm, Agent
from core import openai_client


class AgentGenerateRepository:
    def __init__(self, agent_name: str, instructions: str):
        self.client = Swarm(client=openai_client)
        self.agent = Agent(
            name=agent_name,
            instructions=instructions,
        )

    def generate(self, query: str):
        user_message = {
            "role": "user",
            "content": query,
        }
        return self.client.run(agent=self.agent, messages=[user_message]).messages[-1][
            "content"
        ]
