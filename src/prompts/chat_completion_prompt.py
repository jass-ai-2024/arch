"""
This module contains prompts for chat completion related to system design.
"""

CHAT_COMPLETION_PROMPT_SYSTEM = """
As an architect, you are tasked with designing a new chat application.
You should design a system design document that outlines the architecture
of the chat application.
"""


CHAT_COMPLETION_PROMPT_USER = """
# Solution Design:
{solution_design_document}

# Researcher Department Comments:
{researcher_comments}
- write a system design document that outlines the architecture of the
application.
Instructions:
1. Analyze the solution design document and research department comments.
2. Provide detailed architectural recommendations for the chat application.
3. Write a system design document that outlines the architecture of the
application.
4. Use the System design document template:
# System design document template:
{sys_des_document_template}
"""
