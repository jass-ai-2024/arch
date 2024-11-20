import hashlib
import json
import uuid


def create_services_json(input_json):
    """
    Process input JSON and transform it to required format with generated IDs
    """
    result = {"services": []}

    # Load input JSON if it's a string
    if isinstance(input_json, str):
        input_json = json.loads(input_json)

    for service in input_json.get("services", []):
        # Generate hash using UUID4
        service_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()
        # Create services catalog for dependency lookups
        services_catalog = {}
        for srv in input_json.get("services", []):
            services_catalog[srv["name"]] = srv
        if "dependencies" in service:
            for dep in service["dependencies"]:
                target_service = dep["target_service"]
                if target_service in services_catalog.keys():
                    dep["full_description_service"] = services_catalog[target_service]
        # Create new service entry
        new_service = {
            "id": service_id,
            "task_desc": service,  # Original service data
            "task_type": "create",  # Default type, can be modified based on requirements
        }

        result["services"].append(new_service)

    return result


if __name__ == "__main__":
	import sys
	input_data = json.loads(sys.stdin.read())
	result = create_services_json(input_data)
	print(json.dumps(result, indent=2))
