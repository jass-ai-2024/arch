import os
from core import prompts
from repository import AgentGenerateRepository


class Pipline:
    def main(self) -> str:
        with open("data" + os.sep + "input_ba.txt", "r") as f:
            context = f.read()

        for _, seq_description in prompts._dict["sections"].items():
            agent = AgentGenerateRepository(
                agent_name=seq_description["agent_name"],
                instructions=seq_description["instructions"],
            )
            output = agent.generate(query=context)

            context += f"\n\n{seq_description['topic']}:\n{output}"

        return context
