import os
import time
from typing import Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.chat_completion_prompt import (CHAT_COMPLETION_PROMPT_SYSTEM,
                                            CHAT_COMPLETION_PROMPT_USER)
from prompts.solution_document_example import SOLUTION_DOCUMENT_EXAMPLE
from prompts.sysdoc_template import SYS_DOC_TEMPLATE

# Environment variables loading
load_dotenv()

# API Settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')

# Keep only one client creation
client = OpenAI(
    api_key=OPENAI_API_KEY,
)


class SysDocSchema(BaseModel):
    """
    SysDocSchema is a Pydantic model that represents the schema for a system document.
    """
    tree_of_thought_architecture: str = Field(..., description="Use Tree-of-Thoughts method to generate the architecture. Step-by-step make a detailed architecture of the system.")
    architecture_details: str = Field(..., description="Generate the full architecture of the system.")
    point_1: str = Field(..., description="Point 1. Introduction (Document Purpose, Terms and Abbreviations, Users and Stakeholders, System Goals and Objectives)")
    point_2: str = Field(..., description="Point 2. Requirements (Functional Requirements, Non-functional Requirements, Constraints)")
    point_3: str = Field(..., description="Point 3. Architectural Design (Overall Architecture, Diagrams)")
    point_4: str = Field(..., description="Point 4. Component Details (Modules and their Interactions, Interfaces)")
    point_5: str = Field(..., description="Point 5. Data Design (Data Model, Data Storage)")
    point_6: str = Field(..., description="Point 6. User Interface (UI Description or API Endpoints)")
    point_7: str = Field(..., description="Point 7. Security (Authentication and Authorization, Encryption, Access Control)")
    point_8: str = Field(..., description="Point 8. Performance and Scalability (Performance Requirements, Scaling Strategies, Load Balancing)")
    point_9: str = Field(..., description="Point 9. External System Integration (APIs and Protocols, Error and Failure Handling)")
    point_10: str = Field(..., description="Point 10. Deployment and Infrastructure (Environments, Tools and Technologies, CI/CD Processes)")
    point_11: str = Field(..., description="Point 11. Testing (Testing Strategy, Testing Tools, Acceptance Criteria)")
    point_12: str = Field(..., description="Point 12. Monitoring and Logging (How the system will be monitored in real-time)")
    point_13: str = Field(..., description="Point 13. Constraints and Assumptions (Technical Constraints)")
    point_14: str = Field(..., description="Point 14. Approvals and Sign-offs (Version History, Responsible Persons)")


def run_inference(system_message: str, user_message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Run inference using OpenAI API and return generated text or error.
    :param system_message: System message
    :param user_message: User message
    :return: Tuple with text and error
    """
    start_time = time.time()
    try:
        response = client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4,
            max_tokens=16000,
            response_format=SysDocSchema,
        )
        elapsed_time = time.time() - start_time
        print(f"Inference time: {elapsed_time:.2f} seconds")
        generated_text = response.choices[0].message.content
        return generated_text, None
    except Exception as e:
        return None, str(e)

def read_file_content(file_path: str) -> str:
    """
    Reads file content from the specified path.
    :param file_path: Path to file
    :return: File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")

def validate_file_path(file_path: str, required: bool = False) -> str:
    """
    Validates file existence and read accessibility.
    
    :param file_path: Path to file
    :param required: Whether the file is required
    :return: Validated file path
    :raises: FileNotFoundError if file doesn't exist and required=True
    """
    if not file_path and not required:
        return ''
    
    if not os.path.isfile(file_path):
        if required:
            raise FileNotFoundError(f"File not found: {file_path}")
        return ''
    
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"No read permission for file: {file_path}")    
    return file_path

def main(solution_document_path: str, system_design_document_path: str, researcher_comments_path: str = None):
    """
    Main function to run the system document generation service.
    """
    try:
        # Validate input files
        solution_path = validate_file_path(solution_document_path)
        output_dir = os.path.dirname(system_design_document_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        comments_path = validate_file_path(researcher_comments_path)

        # Read solution document
        solution_document = (
            read_file_content(solution_path) if solution_path 
            else SOLUTION_DOCUMENT_EXAMPLE
        )
        
        # Read researcher comments
        researcher_comments = (
            read_file_content(comments_path) if comments_path 
            else "Great job, everything is correct!"
        )

        # Form user message
        user_message = CHAT_COMPLETION_PROMPT_USER.format(
            solution_design_document=solution_document,
            researcher_comments=researcher_comments,
            sys_des_document_template=SYS_DOC_TEMPLATE
        )

        system_message = CHAT_COMPLETION_PROMPT_SYSTEM
        summary, error = run_inference(system_message, user_message)
        if error:
            print(f"An error occurred: {error}")
            return

        # 4. Save generated text to file
        with open(system_design_document_path, "w", encoding="utf-8") as file:
            file.write(str(summary))
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate system documentation')
    parser.add_argument('--solution', type=str, default='',
                        help='Path to solution document file')
    parser.add_argument('--output', type=str, required=True,
                        help='Path to output system design document file')
    parser.add_argument('--comments', type=str, default='',
                        help='Path to researcher comments file')
    
    args = parser.parse_args()
    
    try:
        main(args.solution, args.output, args.comments)
    except (FileNotFoundError, PermissionError) as e:
        print(f"File operation error: {e}")
        sys.exit(1)