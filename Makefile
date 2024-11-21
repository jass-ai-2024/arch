
EXAMPLE_DIR = data/toxic
# EXAMPLE_DIR = instagram_task

create_solution:
	PYTHONPATH="." python src/service/pipeline_service.py < ${EXAMPLE_DIR}/analytic_pd_v0.md &> ${EXAMPLE_DIR}/solution.md
extract_ml_part:
	PYTHONPATH="." python src/extract_ml_part_for_research.py --input ${EXAMPLE_DIR}/solution.md --output-dir ${EXAMPLE_DIR}
create_system_doc:
	PYTHONPATH="." python src/service/sysdoc_generator_service.py --solution ${EXAMPLE_DIR}/solution.md --output ${EXAMPLE_DIR}/system_design_doc_v0.md --comments ${EXAMPLE_DIR}/research_result_0.txt

create_div2services:
	cat ${EXAMPLE_DIR}/solution.md ${EXAMPLE_DIR}/system_design_doc_v0.md | PYTHONPATH="." python src/service/div2services_agent.py 1> ${EXAMPLE_DIR}/div2services_full.json
prepare_json2dev:
	PYTHONPATH="." python src/prepare_json2dev.py < ${EXAMPLE_DIR}/div2services_full.json &> ${EXAMPLE_DIR}/arch_services_v0.json
create_scheme:
	PYTHONPATH="." python scheme/scheme_generator.py < ${EXAMPLE_DIR}/div2services_full.json &> ${EXAMPLE_DIR}/scheme.log

