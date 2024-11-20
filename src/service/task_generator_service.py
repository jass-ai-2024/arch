import json
import logging
from typing import Dict, List

from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class TaskGeneratorService:
    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(model_name=model_name)
        self.output_parser = CommaSeparatedListOutputParser()
        # self.logger = logging.getLogger(__name__)

    def generate_thoughts(
        self, service_description: str, n_candidates: int = 5
    ) -> List[str]:
        # self.logger.info(f"Generating {n_candidates} initial thoughts for the service")
        # self.logger.debug(f"Service description: {service_description}")

        thought_prompt = PromptTemplate(
            template="""Based on the service description, generate {n_candidates} different approaches to task decomposition.
            Service description: {service_description}
            
            Output only a list of approaches, separated by commas.""",
            input_variables=["service_description", "n_candidates"],
        )

        thoughts = self.llm.invoke(
            thought_prompt.format(
                service_description=service_description, n_candidates=n_candidates
            )
        )

        parsed_thoughts = self.output_parser.parse(thoughts.content)
        # self.logger.info(f"Generated {len(parsed_thoughts)} thoughts")
        # for i, thought in enumerate(parsed_thoughts, 1):
            # self.logger.debug(f"Thought {i}: {thought}")

        return parsed_thoughts

    def evaluate_thought(self, thought: str, service_description: str) -> str:
        # self.logger.info(f"Evaluating thought: {thought[:50]}...")

        eval_prompt = PromptTemplate(
            template="""Evaluate the following task decomposition approach:
            Service description: {service_description}
            Approach: {thought}
            
            Rate as: "certainly" (if the approach will definitely lead to good decomposition),
            "possibly" (if the approach might lead to good decomposition),
            "impossible" (if the approach is definitely not suitable).
            
            Output only one evaluation word.""",
            input_variables=["thought", "service_description"],
        )

        evaluation = self.llm.invoke(
            eval_prompt.format(thought=thought, service_description=service_description)
        )

        result = evaluation.content.strip().lower()
        # self.logger.info(f"Evaluation result: {result}")
        return result

    def generate_tasks_from_thought(
        self, thought: str, service_description: str
    ) -> List[Dict]:
        # self.logger.info("Generating specific tasks based on the chosen approach")
        # self.logger.debug(f"Using approach: {thought}")

        task_prompt = PromptTemplate(
            template="""Based on the chosen approach, generate a list of specific technical tasks for developers.
            Service description: {service_description}
            Approach: {thought}
            
            Output the list of tasks in JSON format. Each task should contain the following fields:
            [
                {{
                    "id": "unique task identifier",
                    "title": "Brief technical task name starting with a verb (Implement, Create, Configure, etc.)",
                    "description": "Detailed technical task description including:
                        - Specific technical requirements with methods, classes, interfaces
                        - Exact list of technologies, libraries and their versions
                        - Input/output data structures with examples
                        - Required API endpoints with request/response formats
                        - Performance and scalability requirements
                        - Specific acceptance criteria and test scenarios",
                    "estimate_hours": "Effort estimate in hours",
                    "dependencies": ["ids of other tasks this task depends on"],
                    "priority": "Task priority (1 - highest, 3 - lowest)",
                    "skills_required": ["list of required technical skills"]
                }}
            ]
            
            Ensure that:
            1. JSON is valid and contains no line breaks within field values
            2. All tasks are specific, measurable, and have clear completion criteria
            3. Each task is independent and can be taken by a separate developer
            4. Tasks do not duplicate functionality
            5. Descriptions contain specific technical details, not general statements""",
            input_variables=["thought", "service_description"],
        )

        tasks = self.llm.invoke(
            task_prompt.format(thought=thought, service_description=service_description)
        )

        try:
            parsed_tasks = json.loads(tasks.content)
        except json.JSONDecodeError as e:
            # self.logger.error(f"JSON parsing error: {e}")
            # self.logger.debug(f"Received content: {tasks.content}")
            return []

        # self.logger.info(f"Generated {len(parsed_tasks)} tasks")
        # for task in parsed_tasks:
            # self.logger.debug(f"Task: {task['title']}")

        return parsed_tasks

    def generate_backlog(self, service_description: str) -> List[Dict]:
        # self.logger.info("Starting task backlog generation")

        # Step 1: Generate initial thoughts
        # self.logger.info("Step 1: Generating initial thoughts")
        thoughts = self.generate_thoughts(service_description)

        # Step 2: BFS to find the best approach
        # self.logger.info("Step 2: Finding the best approach through BFS")
        best_thought = None
        best_evaluation_count = 0

        for i, thought in enumerate(thoughts, 1):
            # self.logger.info(f"Evaluating thought {i}/{len(thoughts)}")
            certainly_count = 0

            for attempt in range(3):
                # self.logger.debug(f"Attempt {attempt + 1}/3")
                evaluation = self.evaluate_thought(thought, service_description)
                if evaluation == "certainly":
                    certainly_count += 1

            # self.logger.info(f"Thought received {certainly_count} 'certainly' evaluations")

            if certainly_count > best_evaluation_count:
                best_evaluation_count = certainly_count
                best_thought = thought
                # self.logger.info(
                    # f"Found a new best approach with {certainly_count} positive evaluations"
                # )

        # Step 3: Generate specific tasks
        # self.logger.info("Step 3: Generating specific tasks")
        if best_thought:
            # self.logger.info("Generating tasks based on the best approach")
            tasks = self.generate_tasks_from_thought(best_thought, service_description)

            # Remove duplicate tasks by id
            unique_tasks = {task["id"]: task for task in tasks}
            tasks = list(unique_tasks.values())

            # Convert tasks to list of dictionaries
            tasks_dicts = []
            for task in tasks:
                task_dict = {
                    "id": task["id"],
                    "title": task["title"],
                    "description": task["description"],
                    "priority": task.get("priority", "medium"),
                    "estimate": task.get("estimate", 0),
                    "dependencies": task.get("dependencies", []),
                }
                tasks_dicts.append(task_dict)
            tasks = tasks_dicts

            # self.logger.info(f"Successfully generated {len(tasks)} unique tasks")

            return tasks

        # self.logger.warning("No suitable approach found for task generation")
        return []


if __name__ == "__main__":
    import sys
    service = TaskGeneratorService()
    test_data = json.loads(sys.stdin.read())
    tasks = service.generate_backlog(test_data)  # Remove f-string since test_data is already a string/dict
    print(json.dumps(tasks, indent=2, ensure_ascii=False))
