from src.core import prompts
from src.repository import AgentGenerateRepository


class Pipeline:
    def run(self, context: str) -> str:
        for seq_description in prompts._dict["sections"].values():
            agent = AgentGenerateRepository(
                agent_name=seq_description["agent_name"],
                instructions=seq_description["instructions"],
            )
            output = agent.generate(query=context)

            context += f"\n\n{seq_description['topic']}:\n{output}"

        return context

if __name__ == "__main__":
    pipeline = Pipeline()
    output = pipeline.run(input())
    print(output)
