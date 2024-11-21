import os
import time
from typing import Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.chat_completion_prompt import (CHAT_COMPLETION_PROMPT_SYSTEM,
                                            CHAT_COMPLETION_PROMPT_USER)
from prompts.solution_document_example import SOLUTION_DOCUMENT_EXAMPLE
from prompts.sysdoc_template import SYS_DOC_TEMPLATE

# Загрузка переменных окружения
load_dotenv()

# Настройки API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = "gpt-4o"

# Оставить только одно создание клиента
client = OpenAI(
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


def run_inference(system_message: str, user_message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Запуск инференса с использованием API OpenAI и возврат сгенерированного текста или ошибки.
    :param system_message: Сообщение от системы
    :param user_message: Сообщение от пользователя
    :return: Кортеж с текстом и ошибкой
    """
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4,
            max_tokens=10000,
        )
        elapsed_time = time.time() - start_time
        print(f"Время на инференс: {elapsed_time:.2f} секунд")
        generated_text = response.choices[0].message.content
        return generated_text, None
    except Exception as e:
        return None, str(e)
    
def read_file_content(file_path: str) -> str:
    """
    Читает содержимое файла по указанному пути.
    :param file_path: Путь к файлу
    :return: Содержимое файла в виде строки
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Ошибка при чтении файла {file_path}: {str(e)}")

def validate_file_path(file_path: str, required: bool = False) -> str:
    """
    Проверяет существование файла и его доступность для чтения.
    
    :param file_path: Путь к файлу
    :param required: Является ли файл обязательным
    :return: Проверенный путь к файлу
    :raises: FileNotFoundError если файл не существует и required=True
    """
    if not file_path and not required:
        return ''
    
    if not os.path.isfile(file_path):
        if required:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        return ''
    
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Нет прав на чтение файла: {file_path}")
    
    return file_path

def main(solution_document_path: str, system_design_document_path: str, researcher_comments_path: str = None):
    """
    Основная функция для запуска сервиса генерации системных документов.
    """
    try:
        # Проверка входных файлов
        solution_path = validate_file_path(solution_document_path)
        output_dir = os.path.dirname(system_design_document_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        comments_path = validate_file_path(researcher_comments_path)

        # Чтение документа решения
        solution_document = (
            read_file_content(solution_path) if solution_path 
            else SOLUTION_DOCUMENT_EXAMPLE
        )
        
        # Чтение комментариев исследователя
        researcher_comments = (
            read_file_content(comments_path) if comments_path 
            else "Красавчики, все верно!"
        )

        # Формирование сообщения пользователя
        user_message = CHAT_COMPLETION_PROMPT_USER.format(
            solution_design_document=solution_document,
            researcher_comments=researcher_comments,
            sys_des_document_template=SYS_DOC_TEMPLATE
        )

        system_message = CHAT_COMPLETION_PROMPT_SYSTEM
        summary, error = run_inference(system_message, user_message)
        if error:
            print(f"Произошла ошибка: {error}")
            return

        # 4. Сохранение сгенерированного текста в файл
        with open(system_design_document_path, "w", encoding="utf-8") as file:
            file.write(str(summary))
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate system documentation')
    parser.add_argument('--solution', type=str, default='',
                        help='Path to solution document file')
    parser.add_argument('--output', type=str, required=True,
                        help='Path to output system design document file')
    parser.add_argument('--comments', type=str, default='',
                        help='Path to researcher comments file')
    
    args = parser.parse_args()
    
    try:
        main(args.solution, args.output, args.comments)
    except (FileNotFoundError, PermissionError) as e:
        print(f"Ошибка при работе с файлами: {e}")
        sys.exit(1)