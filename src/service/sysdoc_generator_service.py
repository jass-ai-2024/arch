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
    Attributes:
        system_doc (str): Сгенерированный текст системного документа. This field is required.
    """
    system_doc: str = Field(..., description="Сгенерированный текст системного документа")


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
    
def main(solution_document_path: str, system_design_document_path: str):
    """
    Основная функция для запуска сервиса генерации системных документов.
    :param solution_document_path: Путь к файлу с документом решения
    :param system_design_document_path: Путь к файлу с документом системного дизайна
    """
    # 1. Обработка PDF файла и извлечение текста
    parsed_text = "Красавчики, все верно!"

    # 3. Запуск асинхронной функции run_inference
    system_message = CHAT_COMPLETION_PROMPT_SYSTEM
    user_message = CHAT_COMPLETION_PROMPT_USER.format(
        solution_design_document=SOLUTION_DOCUMENT_EXAMPLE,
        researcher_comments=parsed_text,
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
    main(solution_document_path, system_design_document_path)
