"""
This module contains a template for a system documentation.

"""

SYS_DOC_TEMPLATE = """
1. Введение:
    1.1. Цель документа:
        - Определение предназначения документа, очень краткое содержание.
    1.2. Список терминов и сокращений:
        - Для единообразия понимания.
    1.3. Пользователи и заинтересованные стороны:
        - Кто будет использовать систему и кому она важна.
    1.4. Цели и задачи системы:
        - Что система должна достичь.

2. Требования:
    2.1. Функциональные требования:
        - Детализация функций, которые система должна выполнять.
    2.2. Нефункциональные требования:
        - Производительность, безопасность, масштабируемость и т.д.
    2.3. Ограничения:
        - Технические, законодательные или другие ограничения.

3. Архитектурный дизайн:
    3.1. Общая архитектура:
        - Высокоуровневая структура системы.
    3.2. Диаграммы:
        - UML-диаграммы, диаграммы компонентов (Mermaid) и т.д.

4. Детализация компонентов:
    4.1. Модули и их взаимодействие:
        - Описание каждого модуля и как они взаимодействуют между собой.
    4.2. Интерфейсы:
        - Определение точек взаимодействия между компонентами.

5. Дизайн данных:
    5.1. Модель данных:
        - ER-диаграммы, схемы баз данных.
    5.2. Хранилища данных:
        - Используемые базы данных, кэши и т.д.

6. Пользовательский интерфейс:
    6.1. Описание UI или API EndPoint:
        - Документация для front-end или back-end.

7. Безопасность:
    7.1. Аутентификация и авторизация:
        - Методы и протоколы.
    7.2. Шифрование:
        - Как и где данные будут шифроваться.
    7.3. Управление доступом:
        - Роли и права пользователей.

8. Производительность и масштабируемость:
    8.1. Требования к производительности:
        - Время отклика, пропускная способность.
    8.2. Стратегии масштабирования:
        - Горизонтальное и вертикальное масштабирование.
    8.3. Балансировка нагрузки:
        - Методы распределения нагрузки между ресурсами.

9. Интеграция с внешними системами:
    9.1. API и протоколы:
        - Используемые интерфейсы для интеграции.
    9.2. Обработка ошибок и отказов:
        - Как система реагирует на сбои внешних сервисов.

10. Развертывание и инфраструктура:
    10.1. Окружения:
        - Разработка, тестирование, производство.
    10.2. Инструменты и технологии:
        - Контейнеризация, оркестрация и т.д.
    10.3. Процессы CI/CD:
        - Автоматизация сборки и развертывания.

11. Тестирование:
    11.1. Стратегия тестирования:
        - Юнит-тесты, интеграционные, системные тесты.
    11.2. Инструменты тестирования:
        - Используемые фреймворки и платформы.
    11.3. Критерии приемки:
        - Что считается успешным тестированием.

12. Мониторинг и логирование:
    12.1. Как система будет отслеживаться в реальном времени.

13. Ограничения и предположения:
    13.1. Технические ограничения:
        - Ограничения оборудования или технологий.

14. Согласования и утверждения:
    14.1. История версий:
        - Изменения в документе.
    14.2. Ответственные лица:
        - Кто подготовил и утвердил документ.
"""
