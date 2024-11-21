# EXAMPLE_DIR = data/toxic
# EXAMPLE_DIR = instagram_task

create_solution:
	# PYTHONPATH="." python src/service/pipeline_service.py < $(INPUT_FILE) > $(SOLUTION_FILE)

extract_ml_part:
	# PYTHONPATH="." python src/extract_ml_part_for_research.py --input $(SOLUTION_FILE) --output-file $(ML_OUTPUT)

create_system_doc:
	# PYTHONPATH="." python src/service/sysdoc_generator_service.py --solution $(SOLUTION_FILE) --output $(SYSTEM_DOC_FILE) --comments $(RESEARCH_FILE)

create_div2services:
	# cat $(SOLUTION_FILE) $(SYSTEM_DOC_FILE) | PYTHONPATH="." python src/service/div2services_agent.py 1> $(DIV_SERVICES_FILE)

prepare_json2dev:
	# PYTHONPATH="." python src/prepare_json2dev.py < $(DIV_SERVICES_FILE) > $(SERVICES_JSON_FILE) 2>&1

create_scheme:
	# PYTHONPATH="." python scheme/scheme_generator.py --output-dir $(SCHEME_DIR) < $(DIV_SERVICES_FILE) > $(SCHEME_LOG_FILE) 2>&1
