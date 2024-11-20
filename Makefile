create_solution:
	PYTHONPATH="src" python src/service/pipeline_service.py < example_end2end_pipeline/ba.txt &> example_end2end_pipeline/solution.txt
create_div2services:
	PYTHONPATH="." python src/service/div2services_agent.py < example_end2end_pipeline/solution.txt &> example_end2end_pipeline/div2services_full.json
create_low_level_tasks:
	PYTHONPATH="." python src/service/task_generator_service.py < example_end2end_pipeline/div2services.json &> example_end2end_pipeline/low_level_tasks.json
