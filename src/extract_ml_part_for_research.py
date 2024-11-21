import re
from pathlib import Path
import os
from openai import OpenAI
import json

from dotenv import load_dotenv
load_dotenv()


def create_ml_research_prompt():
    return """You are an expert ML researcher. Extract ONLY THE MAIN research-focused machine learning task from the solution description.
    Focus exclusively on the core ML research problem that needs investigation. Ignore secondary or auxiliary ML tasks.
    
    The main research task must:
    - Be the central ML problem that directly addresses the primary business goal
    - Focus on investigating ML approaches, not implementing them
    - Belong to a specific ML domain (CV, NLP, RecSys, etc.)
    - Have clear, measurable research outcomes
    - Be a research-oriented ML problem, not a development or engineering task
    - Include specific metrics for evaluating research findings
    
    Examples:
    - If the solution involves recommendation system with user authentication and logging:
        ✓ MAIN TASK: Research optimal recommendation algorithms for the specific use case
        ✗ SKIP: User behavior analysis, logging system optimization
    
    - If the solution involves computer vision with data preprocessing:
        ✓ MAIN TASK: Investigate best CV architectures for the specific recognition task
        ✗ SKIP: Data augmentation research, preprocessing optimization
    
    Provide the main task in JSON format with the following structure:
    
    {
        "research_tasks": [  // Should contain only ONE task
            {
                "task_name": "string",
                "ml_domain": "string",  // e.g., "NLP", "CV", "RecSys", "TimeSeries", etc.
                "description": "string",
                "technical_constraints": [
                    {
                        "constraint_type": "string",  // e.g., "performance", "accuracy", "latency"
                        "description": "string"
                    }
                ],
                "evaluation_metrics": ["string"],  // e.g., ["F1-score", "MAP@K", "RMSE"]
                "success_criteria": ["string"]     // e.g., ["Achieve 95% accuracy", "Latency under 100ms"]
            }
        ]
    }"""

def get_research_tasks(solution_description: str) -> dict:
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": create_ml_research_prompt()},
            {"role": "user", "content": solution_description},
        ],
        response_format={"type": "json_object"},
    )
    
    return json.loads(response.choices[0].message.content)

def save_ml_research_doc(input_file: str, output_file: str = 'research_task.txt') -> str:
    """
    Creates a research document focusing on strategic ML tasks.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    research_tasks = get_research_tasks(content)
    
    # Format content
    formatted_content = []
    for idx, task in enumerate(research_tasks['research_tasks'], 1):
        formatted_content.extend([
            f"ML Task #{idx}: {task['task_name']}",
            "=" * 50,
            f"ML Domain: {task['ml_domain']}",
            f"\nDescription:\n{task['description']}",
            "\nTechnical Constraints:",
            *[f"- {constraint['description']}" for constraint in task['technical_constraints']],
            "\nEvaluation Metrics:",
            *[f"- {metric}" for metric in task['evaluation_metrics']],
            "\nSuccess Criteria:",
            *[f"- {criterion}" for criterion in task['success_criteria']],
            "\n" + "-" * 50 + "\n"
        ])
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(formatted_content))
    
    return output_file

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract ML content from system design document')
    parser.add_argument('--input', type=str, default='solution.txt',
                        help='Path to input solution document')
    parser.add_argument('--output-file', type=str, default='research_task.txt',
                        help='Path to output ML document')
    
    args = parser.parse_args()
    
    output_path = save_ml_research_doc(args.input, args.output_file)
    print(f"ML design document created: {output_path}")
