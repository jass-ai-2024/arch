import os
from service.task_generator_service import TaskGeneratorService


def test_task_generator():
    # Инициализация сервиса с API ключом из переменной окружения
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Необходимо установить переменную окружения OPENAI_API_KEY")

    service = TaskGeneratorService(api_key)

    # Тестовое описание архитектуры
    description = """
    Необходимо разработать систему управления заказами для ресторана, которая будет включать:
    - Управление меню и категориями блюд
    - Прием и обработку заказов
    - Управление столиками и бронированием
    - Интеграцию с кухней
    - Систему лояльности клиентов
    """

    # Генерация задач
    tasks = service.decompose_architecture(description)

    # Валидация задач
    validated_tasks = service.validate_tasks(tasks, description)

    # Сохранение результатов в файл
    with open("architecture_tasks.txt", "w", encoding="utf-8") as f:
        f.write("=== Сгенерированные архитектурные задачи ===\n\n")
        for i, task in enumerate(validated_tasks, 1):
            f.write(f"Задача {i}:\n")
            f.write(f"Название: {task.title}\n")
            f.write(f"Описание: {task.description}\n")
            f.write(f"Приоритет: {task.priority}\n")
            f.write(f"Зависимости: {', '.join(task.dependencies)}\n")
            f.write("\n" + "-" * 50 + "\n\n")


if __name__ == "__main__":
    test_task_generator()
