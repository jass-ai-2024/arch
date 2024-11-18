from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from swarm import Swarm, Agent

router = APIRouter(prefix="/v1", tags=["architecture"])

class ArchitectureRequest(BaseModel):
    project_description: str
    requirements: List[str]

class ArchitectureResponse(BaseModel):
    deployment: Dict[str, str]
    testing: Dict[str, str]
    research: Dict[str, str]

def create_deployment_agent():
    return Agent(
        name="Deployment Architect",
        instructions="""You are an expert in software deployment architecture.
        Analyze requirements and provide detailed deployment solutions including:
        - Infrastructure choices
        - Containerization strategy
        - Scaling approach
        - Service mesh considerations
        Provide clear, practical recommendations."""
    )

def create_testing_agent():
    return Agent(
        name="Testing Architect",
        instructions="""You are an expert in software testing architecture.
        Analyze requirements and provide comprehensive testing strategies including:
        - Testing levels (unit, integration, e2e)
        - Test automation approach
        - Testing tools and frameworks
        - Quality metrics and coverage
        Provide practical testing architecture solutions."""
    )

def create_research_agent():
    return Agent(
        name="Research Architect",
        instructions="""You are an expert in software research and innovation.
        Analyze requirements and provide research-oriented solutions including:
        - Technology evaluation
        - Proof of concept approaches
        - Innovation opportunities
        - Risk assessment
        Provide forward-looking architectural recommendations."""
    )

@router.post("/generate-architecture", response_model=ArchitectureResponse)
async def generate_architecture(request: ArchitectureRequest) -> ArchitectureResponse:
    """Generate architectural solution based on user input"""
    try:
        client = Swarm()
        
        # Initialize agents
        deployment_agent = create_deployment_agent()
        testing_agent = create_testing_agent()
        research_agent = create_research_agent()
        
        # Prepare message for agents
        user_message = {
            "role": "user",
            "content": f"""Project Description: {request.project_description}
            Requirements:
            {chr(10).join(f'- {req}' for req in request.requirements)}
            
            Please provide detailed architectural recommendations for your specific area."""
        }
        
        # Get responses from each agent
        deployment_response = client.run(agent=deployment_agent, messages=[user_message])
        testing_response = client.run(agent=testing_agent, messages=[user_message])
        research_response = client.run(agent=research_agent, messages=[user_message])
        
        return ArchitectureResponse(
            deployment={"solution": deployment_response.messages[-1]["content"]},
            testing={"solution": testing_response.messages[-1]["content"]},
            research={"solution": research_response.messages[-1]["content"]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate architecture: {str(e)}")
