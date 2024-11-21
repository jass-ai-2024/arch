#!/bin/bash

while true; do
    # Поиск последнего файла analytic_v*.txt
    LATEST_ANALYTIC=$(ls -v analytic/analytic_*.txt 2>/dev/null | tail -n1)
    
    if [ -z "$LATEST_ANALYTIC" ]; then
        echo "Waiting for analytic files..."
        sleep 10
        continue
    fi
    
    # Извлечение номера версии (только цифра)
    VERSION=$(echo $LATEST_ANALYTIC | grep -o '[0-9]*' | sed 's/v//' | head -1)
    
    # Определение имен файлов с версией
    SOLUTION="architect/arch_solution_${VERSION}.md"
    ML_OUTPUT_DIR="research/research_task_${VERSION}.txt"
    SYSTEM_DOC="architect/arch_system_doc_${VERSION}.md"
    RESEARCH_RESULT="research/research_result_${VERSION}.txt"
    DIV_SERVICES="architect/arch_div_services_${VERSION}.json"
    SERVICES_JSON="architect/arch_services_${VERSION}.json"
    SCHEME_LOG="architect/arch_scheme_${VERSION}.log"
    SCHEME_DIR="architect"
    
    # Проверка, был ли уже обработан этот файл
    # if [ -f "$SERVICES_JSON" ]; then
    #     echo "Services JSON file $SERVICES_JSON already exists"
    #     sleep 10
    #     continue
    # fi
    
    echo "Processing $LATEST_ANALYTIC..."
    
    # Выполнение команд make с новыми именами файлов
    EXAMPLE_DIR=architect INPUT_FILE=$LATEST_ANALYTIC SOLUTION_FILE=$SOLUTION ML_OUTPUT=$ML_OUTPUT_DIR SYSTEM_DOC_FILE=$SYSTEM_DOC RESEARCH_FILE=$RESEARCH_RESULT DIV_SERVICES_FILE=$DIV_SERVICES SERVICES_JSON_FILE=$SERVICES_JSON SCHEME_LOG_FILE=$SCHEME_LOG SCHEME_DIR=$SCHEME_DIR make create_solution extract_ml_part
    # EXAMPLE_DIR=architect INPUT_FILE=$LATEST_ANALYTIC SOLUTION_FILE=$SOLUTION ML_OUTPUT=$ML_OUTPUT_DIR SYSTEM_DOC_FILE=$SYSTEM_DOC RESEARCH_FILE=$RESEARCH_RESULT DIV_SERVICES_FILE=$DIV_SERVICES SERVICES_JSON_FILE=$SERVICES_JSON SCHEME_LOG_FILE=$SCHEME_LOG make extract_ml_part
    echo "Get research result..."
    sleep 10
    cp research_result_0.txt $RESEARCH_RESULT
    if [ ! -f "$RESEARCH_RESULT" ]; then
        echo "Research result file $RESEARCH_RESULT not found"
        sleep 10
        continue
    fi
    
    EXAMPLE_DIR=architect INPUT_FILE=$LATEST_ANALYTIC SOLUTION_FILE=$SOLUTION ML_OUTPUT=$ML_OUTPUT_DIR SYSTEM_DOC_FILE=$SYSTEM_DOC RESEARCH_FILE=$RESEARCH_RESULT DIV_SERVICES_FILE=$DIV_SERVICES SERVICES_JSON_FILE=$SERVICES_JSON SCHEME_LOG_FILE=$SCHEME_LOG SCHEME_DIR=$SCHEME_DIR make create_system_doc create_div2services prepare_json2dev create_scheme

    # EXAMPLE_DIR=architect INPUT_FILE=$LATEST_ANALYTIC SOLUTION_FILE=$SOLUTION ML_OUTPUT=$ML_OUTPUT_DIR SYSTEM_DOC_FILE=$SYSTEM_DOC RESEARCH_FILE=$RESEARCH_RESULT DIV_SERVICES_FILE=$DIV_SERVICES SERVICES_JSON_FILE=$SERVICES_JSON SCHEME_LOG_FILE=$SCHEME_LOG SCHEME_DIR=$SCHEME_DIR make create_scheme
    
    echo "Completed processing version $VERSION"
    sleep 10
done
