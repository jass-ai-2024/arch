#!/bin/bash

# Директория для мониторинга
WATCH_DIR="analitic"
# Шаблон файла для отслеживания
FILE_PATTERN="analitic_v[0-9]*.txt"

# Создаем директорию, если она не существует
mkdir -p "$WATCH_DIR"

echo "Starting deployment script..."
echo "Watching directory: $WATCH_DIR"

# Переменная для хранения последнего обработанного файла
LAST_PROCESSED=""

while true; do
    # Находим последний файл (с самым большим номером версии)
    LATEST_FILE=$(ls -v "$WATCH_DIR"/$FILE_PATTERN 2>/dev/null | tail -n 1)
    
    # Проверяем, есть ли новый файл и отличается ли он от последнего обработанного
    if [ -n "$LATEST_FILE" ] && [ "$LATEST_FILE" != "$LAST_PROCESSED" ]; then
        echo "Found new analytics file: $LATEST_FILE"
        
        # Получаем номер версии из имени файла
        version=$(echo "$LATEST_FILE" | grep -o '[0-9]\+')
        echo "Processing version: $version"
        
        # Копируем файл в EXAMPLE_DIR как ba.txt
        cp "$LATEST_FILE" "iris_dataset_service/ba.txt"
        
        # Последовательно запускаем команды из Makefile
        echo "Starting pipeline processing..."
        make create_solution
        make create_div2services
        make prepare_json2dev
        make create_scheme
        
        # Перемещаем обработанный файл в архив
        mkdir -p "$WATCH_DIR/processed"
        mv "$LATEST_FILE" "$WATCH_DIR/processed"
        
        # Обновляем переменную последнего обработанного файла
        LAST_PROCESSED="$LATEST_FILE"
    fi
done
