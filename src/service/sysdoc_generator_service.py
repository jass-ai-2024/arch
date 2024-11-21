import asyncio
import os
import time
from typing import Optional, Tuple

import nest_asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.chat_completion_prompt import (CHAT_COMPLETION_PROMPT_SYSTEM,
                                            CHAT_COMPLETION_PROMPT_USER)
from prompts.solution_document_example import SOLUTION_DOCUMENT_EXAMPLE
from prompts.sysdoc_template import SYS_DOC_TEMPLATE

client = AsyncOpenAI()

# Загрузка переменных окружения
load_dotenv()

# Настройки API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')

# Создание клиента OpenAI
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
)


class SysDocSchema(BaseModel):
    """
    SysDocSchema is a Pydantic model that represents the schema for a system document.
    """
    point_1: str = Field(..., description="Сгенерированный текст системного документа. Пункт 1. Введение (Цель документа, Список терминов и сокращений, Пользователи и заинтересованные стороны, Цели и задачи системы)")
    point_2: str = Field(..., description="Сгенерированный текст системного документа. Пункт 2. Требования (Функциональные требования, Нефункциональные требования, Ограничения)")
    point_3: str = Field(..., description="Сгенерированный текст системного документа. Пункт 3. Архитектурный дизайн (Общая архитектура, Диаграммы)")
    point_4: str = Field(..., description="Сгенерированный текст системного документа. Пункт 4. Детализация компонентов (Модули и их взаимодействие, Интерфейсы)")
    point_5: str = Field(..., description="Сгенерированный текст системного документа. Пункт 5. Дизайн данных (Модель данных, Хранилища данных)")
    point_6: str = Field(..., description="Сгенерированный текст системного документа. Пункт 6. Пользовательский интерфейс (Описание UI или API EndPoint)")
    point_7: str = Field(..., description="Сгенерированный текст системного документа. Пункт 7. Безопасность (Аутентификация и авторизация, Шифрование, Управление доступом)")
    point_8: str = Field(..., description="Сгенерированный текст системного документа. Пункт 8. Производительность и масштабируемость (Требования к производительности, Стратегии масштабирования, Балансировка нагрузки)")
    point_9: str = Field(..., description="Сгенерированный текст системного документа. Пункт 9. Интеграция с внешними системами (API и протоколы, Обработка ошибок и отказов)")
    point_10: str = Field(..., description="Сгенерированный текст системного документа. Пункт 10. Развертывание и инфраструктура (Окружения, Инструменты и технологии, Процессы CI/CD)")
    point_11: str = Field(..., description="Сгенерированный текст системного документа. Пункт 11. Тестирование (Стратегия тестирования, Инструменты тестирования, Критерии приемки)")
    point_12: str = Field(..., description="Сгенерированный текст системного документа. Пункт 12. Мониторинг и логирование (Как система будет отслеживаться в реальном времени)")
    point_13: str = Field(..., description="Сгенерированный текст системного документа. Пункт 13. Ограничения и предположения (Технические ограничения)")
    point_14: str = Field(..., description="Сгенерированный текст системного документа. Пункт 14. Согласования и утверждения (История версий, Ответственные лица)")


async def run_inference(system_message: str, user_message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Запуск инференса с использованием API OpenAI и возврат сгенерированного текста или ошибки.
    :param system_message: Сообщение от системы
    :param user_message: Сообщение от пользователя
    :return: Кортеж с текстом и ошибкой
    """
    start_time = time.time()
    try:
        response = await client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4,
            max_tokens=10000,
            response_format=SysDocSchema,
        )
        elapsed_time = time.time() - start_time
        print(f"Время на инференс: {elapsed_time:.2f} секунд")
        generated_text = response.choices[0].message.parsed.model_dump()
        return generated_text, None
    except Exception as e:
        return None, str(e)
    
def main(solution_document_path: str, system_design_document_path: str, researcher_comments_path: str):
    """
    Основная функция для запуска сервиса генерации системных документов.
    :param solution_document_path: Путь к файлу с документом решения
    :param system_design_document_path: Путь к файлу с документом системного дизайна
    """
    # 1. Обработка файла и извлечение текста
    parsed_text = "Красавчики, все верно!"
    researcher_comments_path = parsed_text

    solution_document = SOLUTION_DOCUMENT_EXAMPLE
    solution_document_path = solution_document
    # 3. Запуск асинхронной функции run_inference
    system_message = CHAT_COMPLETION_PROMPT_SYSTEM
    user_message = CHAT_COMPLETION_PROMPT_USER.format(
        solution_design_document=solution_document_path,  # поменять тут
        researcher_comments=researcher_comments_path,  # поменять тут
        sys_des_document_template=SYS_DOC_TEMPLATE
    )
    nest_asyncio.apply()
    # 3. Запуск асинхронной функции run_inference
    summary, error = asyncio.run(run_inference(system_message, user_message))
    if error:
        print(f"Произошла ошибка: {error}")
        return
    # 3. Парсинг сгенерированного резюме и удаление форматирования Markdown
    print(summary)
    print(len(summary))

    # 4. Сохранение сгенерированного текста в файл
    with open(system_design_document_path, "w", encoding="utf-8") as file:
        file.write(str(summary))


if __name__ == "__main__":
    solution_document_path = ""
    system_design_document_path = "data/final_sysdoc.json"
    researcher_comments_path = ""
    
    main(solution_document_path,
         system_design_document_path,
         researcher_comments_path)
