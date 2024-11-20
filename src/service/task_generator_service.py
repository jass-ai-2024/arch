from typing import List, Dict, Optional
from dataclasses import dataclass
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from pydantic import BaseModel, Field
from core import configs
import json
import logging
import re


@dataclass
class ThoughtNode:
    content: str
    variants: List[str]
    selected_variant: Optional[str] = None
    children: List["ThoughtNode"] = None
    confidence: float = 0.0


class ArchitectureTask(BaseModel):
    title: str = Field(description="Название задачи")
    description: str = Field(description="Описание задачи")
    priority: int = Field(description="Приоритет от 1 до 5")
    dependencies: List[str] = Field(description="Зависимости")


class TaskGeneratorService:
    def __init__(self, **kwargs):
        self.llm = ChatOpenAI(
            temperature=0.7, model_name="gpt-4", openai_api_key=configs.GPT_TOKEN
        )

    def _generate_thought_variants(
        self, prompt: str, n_variants: str = "3"
    ) -> List[str]:
        """Генерирует несколько вариантов мысли для заданного промпта"""
        chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""
                Сгенерируй {n_variants} различных варианта ответа на следующий вопрос:
                
                {prompt}
                
                Варианты должны быть разными по подходу и детализации.
                """,
                input_variables=["prompt", "n_variants"],
            ),
        )

        result = chain.run(prompt=prompt, n_variants=n_variants)
        return [v.strip() for v in result.split("\n") if v.strip()]

    def _evaluate_variants(self, variants: List[str], context: str) -> str:
        """Оценивает варианты и выбирает лучший"""
        chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""
                Оцени следующие варианты решения в контексте:
                
                Контекст: {context}
                
                Варианты:
                {variants}
                
                Выбери лучший вариант и объясни почему.
                """,
                input_variables=["variants", "context"],
            ),
        )

        result = chain.run(variants="\n".join(variants), context=context)
        return result.strip()

    def _json_to_description(self, json_data: Dict) -> str:
        """Преобразует JSON в текстовое описание"""
        desc = f"Сервис: {json_data['name']}\n"
        desc += f"Тип: {json_data['service_type']}\n"
        desc += f"Описание: {json_data['description']}\n"

        if json_data.get("dependencies"):
            desc += "Зависимости:\n"
            for dep in json_data["dependencies"]:
                desc += f"- {dep['target_service']}: {dep['description']}\n"

        if json_data.get("database_requirements"):
            db = json_data["database_requirements"]
            desc += f"База данных: {db['type']}\n"
            desc += f"Описание БД: {db['description']}\n"

        return desc

    def decompose_architecture(self, description: Dict) -> List[ArchitectureTask]:
        """
        Декомпозирует архитектурное описание на задачи используя Tree of Thoughts.
        Принимает описание сервиса в формате JSON:
        {
            "name": "UserProfileService",
            "service_type": "crud",
            "description": "Handles user profiles including authentication, personal information, and preferences management.",
            "dependencies": [],
            "database_requirements": {
                "type": "relational",
                "description": "Stores user profile data, credentials, and preferences.",
                "required": true
            }
        }
        """
        # Преобразуем JSON в текстовое описание
        description_text = self._json_to_description(description)
        # Шаг 1: Определение основных аспектов архитектуры
        root = ThoughtNode(
            content="Какие основные аспекты архитектуры нужно рассмотреть?",
            variants=self._generate_thought_variants(
                "Определи основные аспекты архитектуры для анализа:\n"
                + description_text
            ),
        )
        root.selected_variant = self._evaluate_variants(root.variants, description_text)

        # Шаг 2: Для каждого аспекта определяем компоненты
        components_node = ThoughtNode(
            content="Какие компоненты нужны для каждого аспекта?",
            variants=self._generate_thought_variants(
                f"Определи необходимые компоненты для реализации:\n{root.selected_variant}",
                n_variants="необходимое",
            ),
        )
        components_node.selected_variant = self._evaluate_variants(
            components_node.variants, root.selected_variant
        )

        # Шаг 3: Определение зависимостей между компонентами
        dependencies_node = ThoughtNode(
            content="Какие зависимости между компонентами?",
            variants=self._generate_thought_variants(
                f"Определи зависимости между компонентами:\n{components_node.selected_variant}"
            ),
        )
        dependencies_node.selected_variant = self._evaluate_variants(
            dependencies_node.variants, components_node.selected_variant
        )

        # Шаг 4: Формирование конкретных задач
        tasks_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""
                На основе проведенного анализа сформируй список конкретных задач.
                
                Архитектурные аспекты:
                {aspects}
                
                Компоненты:
                {components}
                
                Зависимости:
                {dependencies}
                
                Для каждой задачи укажи следующие поля:
                - title: Название задачи
                - description: Описание задачи
                - priority: Приоритет (1-5)
                - dependencies: Список зависимостей от других задач
                
                Формат: JSON список объектов ArchitectureTask с полями title, description, priority, dependencies.
                
                Пример:
                [
                    {{
                        "title": "Разработка модуля аутентификации",
                        "description": "Создать модуль для управления аутентификацией пользователей.",
                        "priority": 1,
                        "dependencies": []
                    }},
                    ...
                ]
                """,
                input_variables=["aspects", "components", "dependencies"],
            ),
        )

        tasks_result = tasks_chain.run(
            aspects=root.selected_variant,
            components=components_node.selected_variant,
            dependencies=dependencies_node.selected_variant,
        )

        # Преобразуем результат в список задач
        logging.debug(f"Полученный JSON: {tasks_result}")

        try:
            tasks_dict = json.loads(tasks_result)
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка декодирования JSON: {e}")

        # Проверяем, что все необходимые поля присутствуют
        for task in tasks_dict:
            if (
                "title" not in task
                or "description" not in task
                or "priority" not in task
                or "dependencies" not in task
            ):
                raise ValueError(f"Отсутствуют необходимые поля в задаче: {task}")

        return [ArchitectureTask(**task) for task in tasks_dict], description_text

    def validate_tasks(
        self, tasks: List[ArchitectureTask], description: str
    ) -> List[ArchitectureTask]:
        """Валидирует и оптимизирует список задач"""
        validation_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""
                Проверь список задач на соответствие исходному описанию архитектуры.
                
                Исходное описание:
                {description}
                
                Задачи:
                {tasks}
                
                Проверь:
                1. Полноту покрытия требований
                2. Корректность зависимостей
                3. Правильность приоритетов
                4. Отсутствие дублирования
                
                Верни только JSON-массив с оптимизированными задачами. Не добавляй никакого дополнительного текста.
                Каждая задача должна содержать поля: title, description, priority, dependencies.
                
                Пример формата ответа:
                [
                    {{
                        "title": "Задача 1",
                        "description": "Описание задачи 1",
                        "priority": 1,
                        "dependencies": []
                    }}
                ]
                """,
                input_variables=["description", "tasks"],
            ),
        )

        result = validation_chain.run(
            description=description, tasks=[task.dict() for task in tasks]
        )

        logging.debug(f"Сырой результат от LLM: {result}")

        # Очистка результата от возможного дополнительного текста
        result = result.strip()

        # Найти первую открывающую и последнюю закрывающую скобки массива
        start_idx = result.find("[")
        end_idx = result.rfind("]") + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError(f"Не удалось найти JSON массив в ответе: {result}")

        json_str = result[start_idx:end_idx]
        logging.debug(f"Извлеченный JSON: {json_str}")

        try:
            validated_tasks = json.loads(json_str)
            # Дополнительная проверка, что мы получили список
            if not isinstance(validated_tasks, list):
                raise ValueError("Результат не является списком")

            return [ArchitectureTask(**task) for task in validated_tasks]
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка декодирования JSON: {e}")
            logging.error(f"Проблемный JSON: {json_str}")
            raise ValueError(f"Не удалось декодировать JSON ответ: {e}")
        except Exception as e:
            logging.error(f"Неожиданная ошибка при обработке задач: {e}")
            raise
