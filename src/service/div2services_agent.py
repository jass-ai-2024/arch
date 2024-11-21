import json

from openai import OpenAI

from src.service.task_generator_service import TaskGeneratorService

client = OpenAI()


def get_agent_response(system_prompt, user_message):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def create_service_decomposition_prompt():
    return """You are an expert in software architecture and system design.
    Analyze the project requirements and decompose the system into independent, loosely-coupled components by:
    
    - Breaking down the system into ONLY essential core components without which the system cannot function
    - Minimizing dependencies and communication between components
    - Ensuring each component has a single clear responsibility
    - Defining simple and standardized interfaces between components
    - Prioritizing component autonomy over tight integration
    - Allowing components to be developed, tested and deployed separately
    
    Important rules for service decomposition:
    - Include ONLY essential services that are critical for basic system functionality
    - Administrative/management services should NOT be separated unless they are core to business requirements
    - Storage/database functionality should be specified in database_requirements rather than as separate services
    - Notification services should ONLY be created as separate services if notifications are a core business function
    
    Provide a detailed breakdown of proposed components in JSON format with the following structure:

    {
        "services": [
            {
                "name": "string", 
                "service_type": "string",
                "description": "string",
                "dependencies": [
                    {
                        "target_service": "string",
                        "interaction_type": "string", 
                        "description": "string"
                    }
                ],
                "database_requirements": {
                    "type": "string",
                    "description": "string",
                    "required": "boolean"
                }
            }
        ]
    }

    Service Types: frontend, backend
    
    Interaction Types: sync_rest, sync_grpc, async_event, async_message, queue_pub_sub, queue_point, stream, batch"""


def get_service_decomposition(project_description: str) -> dict:
    """
    Analyzes project requirements and generates microservices decomposition strategy.

    Example:
        project_description = "Chat bot for sales assistant that helps customers find products,
                             answers questions about pricing and availability, processes orders,
                             and provides after-sales support through natural language interactions"

        This will generate a decomposition with services like:
        - ChatBotService for natural language processing
        - SalesDataService for product/pricing data
        - OrderingService for order management
        - UserProfileService for customer data
        - NotificationService for customer communications
        etc.

    Args:
        project_description (str): Detailed description of the project requirements and goals

    Returns:
        dict: JSON structure containing microservices decomposition strategy
    """
    deployment_response = get_agent_response(
        system_prompt=create_service_decomposition_prompt(),
        user_message=f"Please analyze the project requirements and provide a detailed microservices decomposition strategy for this project: {project_description}",
    )

    parsed_response = json.loads(deployment_response)
    return parsed_response


if __name__ == "__main__":
    project_desc = input()
    # print(json.dumps(get_service_decomposition(project_desc), indent=2))
    services_data_json = get_service_decomposition(project_desc)
    for ind, service_data in enumerate(services_data_json["services"]):
        service = TaskGeneratorService()
        tasks = service.generate_backlog(
            json.dumps(service_data, indent=2, ensure_ascii=False)
        )
        services_data_json["services"][ind]["low_level_tasks"] = tasks
    print(json.dumps(services_data_json, indent=2, ensure_ascii=False))
