
EXAMPLE_DIR = iris_dataset_service
# EXAMPLE_DIR = instagram_task

create_solution:
	PYTHONPATH="." python src/service/pipeline_service.py < ${EXAMPLE_DIR}/ba.txt &> ${EXAMPLE_DIR}/solution.txt
create_div2services: create_solution
	PYTHONPATH="." python src/service/div2services_agent.py < ${EXAMPLE_DIR}/solution.txt &> ${EXAMPLE_DIR}/div2services_full.json
prepare_json2dev:
	PYTHONPATH="." python src/prepare_json2dev.py < ${EXAMPLE_DIR}/div2services_full.json &> ${EXAMPLE_DIR}/full_json.json
create_scheme:
	PYTHONPATH="." python scheme/scheme_generator.py < ${EXAMPLE_DIR}/div2services_full.json &> ${EXAMPLE_DIR}/scheme.log
