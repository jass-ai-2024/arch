from typing import List, Dict, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser
import json
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class TaskGeneratorService:
    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(model_name=model_name)
        self.output_parser = CommaSeparatedListOutputParser()
        self.logger = logging.getLogger(__name__)

    def generate_thoughts(
        self, service_description: str, n_candidates: int = 5
    ) -> List[str]:
        self.logger.info(f"Генерация {n_candidates} начальных мыслей для сервиса")
        self.logger.debug(f"Описание сервиса: {service_description}")

        thought_prompt = PromptTemplate(
            template="""На основе описания сервиса, сгенерируйте {n_candidates} различных подходов к декомпозиции задач.
            Описание сервиса: {service_description}
            
            Выведите только список подходов, разделенных запятыми.""",
            input_variables=["service_description", "n_candidates"],
        )

        thoughts = self.llm.invoke(
            thought_prompt.format(
                service_description=service_description, n_candidates=n_candidates
            )
        )

        parsed_thoughts = self.output_parser.parse(thoughts.content)
        self.logger.info(f"Сгенерировано {len(parsed_thoughts)} мыслей")
        for i, thought in enumerate(parsed_thoughts, 1):
            self.logger.debug(f"Мысль {i}: {thought}")

        return parsed_thoughts

    def evaluate_thought(self, thought: str, service_description: str) -> str:
        self.logger.info(f"Оценка мысли: {thought[:50]}...")

        eval_prompt = PromptTemplate(
            template="""Оцените следующий подход к декомпозиции задач:
            Описание сервиса: {service_description}
            Подход: {thought}
            
            Оцените как: "конечно" (если подход определенно приведет к хорошей декомпозиции),
            "возможно" (если подход может привести к хорошей декомпозиции),
            "невозможно" (если подход точно не подходит).
            
            Выведите только одно слово-оценку.""",
            input_variables=["thought", "service_description"],
        )

        evaluation = self.llm.invoke(
            eval_prompt.format(thought=thought, service_description=service_description)
        )

        result = evaluation.content.strip().lower()
        self.logger.info(f"Результат оценки: {result}")
        return result

    def generate_tasks_from_thought(
        self, thought: str, service_description: str
    ) -> List[Dict]:
        self.logger.info("Генерация конкретных задач на основе выбранного подхода")
        self.logger.debug(f"Используемый подход: {thought}")

        task_prompt = PromptTemplate(
            template="""На основе выбранного подхода сгенерируйте список конкретных технических задач для разработчиков.
            Описание сервиса: {service_description}
            Подход: {thought}
            
            Выведите список задач в формате JSON. Каждая задача должна содержать следующие поля:
            [
                {{
                    "id": "уникальный идентификатор задачи",
                    "title": "Краткое техническое название задачи, начинающееся с глагола (Реализовать, Создать, Настроить и т.д.)",
                    "description": "Подробное техническое описание задачи, включающее:
                        - Конкретные технические требования с указанием методов, классов, интерфейсов
                        - Точный список используемых технологий, библиотек и их версий
                        - Структуры входных и выходных данных с примерами
                        - Необходимые API endpoints с форматами запросов/ответов
                        - Требования к производительности и масштабируемости
                        - Конкретные критерии приемки и тестовые сценарии",
                    "estimate_hours": "Оценка трудозатрат в часах",
                    "dependencies": ["id других задач, от которых зависит эта задача"],
                    "priority": "Приоритет задачи (1 - высший, 3 - низший)",
                    "skills_required": ["список необходимых технических навыков"]
                }}
            ]
            
            Убедитесь, что:
            1. JSON валиден и не содержит переносов строк внутри значений полей
            2. Все задачи конкретны, измеримы и имеют четкие критерии завершения
            3. Каждая задача независима и может быть взята в работу отдельным разработчиком
            4. Задачи не дублируют функциональность друг друга
            5. Описания содержат конкретные технические детали, а не общие формулировки""",
            input_variables=["thought", "service_description"],
        )

        tasks = self.llm.invoke(
            task_prompt.format(thought=thought, service_description=service_description)
        )

        try:
            parsed_tasks = json.loads(tasks.content)
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            self.logger.debug(f"Полученный контент: {tasks.content}")
            return []

        self.logger.info(f"Сгенерировано {len(parsed_tasks)} задач")
        for task in parsed_tasks:
            self.logger.debug(f"Задача: {task['title']}")

        return parsed_tasks

    def generate_backlog(self, service_description: str) -> List[Dict]:
        self.logger.info("Начало генерации беклога задач")

        # Шаг 1: Генерация начальных мыслей
        self.logger.info("Шаг 1: Генерация начальных мыслей")
        thoughts = self.generate_thoughts(service_description)

        # Шаг 2: BFS для поиска лучшего подхода
        self.logger.info("Шаг 2: Поиск лучшего подхода через BFS")
        best_thought = None
        best_evaluation_count = 0

        for i, thought in enumerate(thoughts, 1):
            self.logger.info(f"Оценка мысли {i}/{len(thoughts)}")
            certainly_count = 0

            for attempt in range(3):
                self.logger.debug(f"Попытка оценки {attempt + 1}/3")
                evaluation = self.evaluate_thought(thought, service_description)
                if evaluation == "конечно":
                    certainly_count += 1

            self.logger.info(f"Мысль получила {certainly_count} оценок 'конечно'")

            if certainly_count > best_evaluation_count:
                best_evaluation_count = certainly_count
                best_thought = thought
                self.logger.info(
                    f"Найден новый лучший подход с {certainly_count} положительными оценками"
                )

        # Шаг 3: Генерация конкретных задач
        self.logger.info("Шаг 3: Генерация конкретных задач")
        if best_thought:
            self.logger.info("Генерация задач на основе лучшего подхода")
            tasks = self.generate_tasks_from_thought(best_thought, service_description)

            # Удаление дублирующихся задач по id
            unique_tasks = {task["id"]: task for task in tasks}
            tasks = list(unique_tasks.values())

            # Преобразование задач в список словарей
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

            self.logger.info(f"Успешно сгенерировано {len(tasks)} уникальных задач")

            return tasks

        self.logger.warning("Не найдено подходящего подхода для генерации задач")
        return []
