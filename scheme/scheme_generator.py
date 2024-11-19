from swarm import Swarm, Agent
import os
import json
import plantuml
import urllib.request

class ArchitectureAgent:
    def __init__(self):
        self.swarm = Swarm()
        # Изменяем URL на более надежный сервер
        self.plantuml_server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/png/')
        
        os.makedirs('output', exist_ok=True)
        
        self.diagram_agent = Agent(
            # client=
            name="Diagram Generator",
            instructions="""You are an expert in software architecture and PlantUML.
            Your task is to generate PlantUML diagrams based on architecture descriptions.
            Always format your response as a raw JSON string (no markdown, no code blocks) with the following structure:
            {
                "c4_context": "@startuml\\n... your PlantUML code ...\\n@enduml",
                "c4_container": "@startuml\\n... your PlantUML code ...\\n@enduml",
                "uml_component": "@startuml\\n... your PlantUML code ...\\n@enduml"
            }
            DO NOT wrap the response in markdown code blocks or ```json tags."""
        )
    
    def generate_diagrams(self, architecture_description):
        messages = [{
        "role": "user",
        "content": f"""Create PlantUML diagrams for this architecture:
        {architecture_description}
        
        Use these clean styles for ALL diagrams:
        @startuml
        ' Basic settings
        skinparam monochrome true
        skinparam shadowing false
        skinparam defaultFontName Arial
        skinparam defaultFontSize 12
        skinparam linetype ortho
        
        ' Spacing and layout
        skinparam nodesep 60
        skinparam ranksep 60
        skinparam padding 10
        skinparam margin 10
        
        ' Component styles
        skinparam component {{
            BackgroundColor White
            BorderColor Black
            FontColor Black
            BorderThickness 1
            FontStyle plain
        }}
        
        ' Rectangle styles
        skinparam rectangle {{
            BackgroundColor White
            BorderColor Black
            FontColor Black
            BorderThickness 1
            FontStyle plain
        }}
        
        ' Database styles
        skinparam database {{
            BackgroundColor White
            BorderColor Black
            FontColor Black
            BorderThickness 1
        }}
        
        ' Arrow styles
        skinparam arrow {{
            Color Black
            FontColor Black
            Thickness 1
        }}
        ' Naming convention for databases
        ' Use service names for databases, with types in square brackets
        ' Example: ChatBotDB [type: document]
        """
        }]
        
        try:
            response = self.swarm.run(
                agent=self.diagram_agent,
                messages=messages
            )
            
            raw_content = response.messages[-1]["content"]
            print("\n=== RAW RESPONSE START ===")
            print(raw_content)
            print("=== RAW RESPONSE END ===\n")
            
            cleaned_content = raw_content.strip()
            if cleaned_content.startswith('```'):
                cleaned_content = cleaned_content.split('\n', 1)[1]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content.rsplit('\n', 1)[0]
            if cleaned_content.startswith('json'):
                cleaned_content = cleaned_content.split('\n', 1)[1]
                    
            diagrams = json.loads(cleaned_content)
            output_files = {}
            
            for diagram_type, puml_code in diagrams.items():
                output_file = os.path.join('output', f"{diagram_type}.png")
                print(f"\nProcessing {diagram_type}...")
                print(f"PlantUML code:\n{puml_code}\n")
                
                try:
                    # Добавляем обработку ошибок PlantUML
                    try:
                        png_data = self.plantuml_server.processes(puml_code)
                    except Exception as puml_error:
                        print(f"PlantUML Error: {str(puml_error)}")
                        print("Trying to fix PlantUML code...")
                        fixed_code = puml_code.replace('\n\n', '\n').strip()
                        png_data = self.plantuml_server.processes(fixed_code)
                    
                    with open(output_file, 'wb') as f:
                        f.write(png_data)
                    output_files[diagram_type] = output_file
                    print(f"Successfully generated {diagram_type}")
                except Exception as e:
                    print(f"Error generating {diagram_type}: {str(e)}")
                    print(f"Full error details: {repr(e)}")
                    continue
                        
            return output_files
                    
        except Exception as e:
            print(f"Error generating diagrams: {str(e)}")
            print(f"Full error details: {repr(e)}")
            return None
def main():
    architecture_description = """
    {
  "services": [
    {
      "name": "UserProfileService",
      "service_type": "crud",
      "description": "Handles user profiles including authentication, personal information, and preferences management.",
      "dependencies": [],
      "database_requirements": {
        "type": "relational",
        "description": "Stores user profile data, credentials, and preferences.",
        "required": true
      }
    },
    {
      "name": "AuthService",
      "service_type": "auth",
      "description": "Manages user authentication and authorization.",
      "dependencies": [
        {
          "target_service": "UserProfileService",
          "interaction_type": "sync_rest",
          "description": "Fetches user credentials to validate login attempts."
        }
      ],
      "database_requirements": {
        "type": "none",
        "description": "External authentication system integration (e.g., OAuth).",
        "required": false
      }
    },
    {
      "name": "ChatBotService",
      "service_type": "processing",
      "description": "Processes user queries and generates responses using AI/ML models.",
      "dependencies": [
        {
          "target_service": "SalesDataService",
          "interaction_type": "sync_rest",
          "description": "Fetches sales data required to generate responses."
        },
        {
          "target_service": "NotificationService",
          "interaction_type": "async_event",
          "description": "Sends events for user response notifications."
        }
      ],
      "database_requirements": {
        "type": "document",
        "description": "Stores conversational histories and context for processing.",
        "required": true
      }
    },
    {
      "name": "SalesDataService",
      "service_type": "database",
      "description": "Manages sales data including product information, pricing, and promotions.",
      "dependencies": [
        {
          "target_service": "ExternalSalesSystem",
          "interaction_type": "async_message",
          "description": "Synchronizes sales data with an external sales system."
        }
      ],
      "database_requirements": {
        "type": "relational",
        "description": "Stores comprehensive sales data, product catalogs, and pricing.",
        "required": true
      }
    },
    {
      "name": "OrderingService",
      "service_type": "crud",
      "description": "Handles order processing, status tracking, and order history management.",
      "dependencies": [
        {
          "target_service": "SalesDataService",
          "interaction_type": "sync_rest",
          "description": "Verifies product availability before processing an order."
        },
        {
          "target_service": "PaymentService",
          "interaction_type": "sync_rest",
          "description": "Initiates payment for orders."
        }
      ],
      "database_requirements": {
        "type": "relational",
        "description": "Stores order details, statuses, and transaction histories.",
        "required": true
      }
    },
    {
      "name": "PaymentService",
      "service_type": "integration",
      "description": "Processes payments and validates transactions with financial institutions.",
      "dependencies": [],
      "database_requirements": {
        "type": "none",
        "description": "Handles transaction processing through third-party systems.",
        "required": false
      }
    },
    {
      "name": "NotificationService",
      "service_type": "notification",
      "description": "Sends notifications to users via different channels (e.g., email, SMS).",
      "dependencies": [],
      "database_requirements": {
        "type": "none",
        "description": "Utilizes third-party communication APIs.",
        "required": false
      }
    },
    {
      "name": "AnalyticsService",
      "service_type": "processing",
      "description": "Collects and analyzes interaction data to generate insights and reports.",
      "dependencies": [
        {
          "target_service": "ChatBotService",
          "interaction_type": "async_event",
          "description": "Gathers data on user interactions for analytics."
        }
      ],
      "database_requirements": {
        "type": "big_data",
        "description": "Stores and processes large volumes of interaction data for analytics.",
        "required": true
      }
    }
  ]
}
    """

    agent = ArchitectureAgent()
    diagram_files = agent.generate_diagrams(architecture_description)
    
    if diagram_files:
        print("\nGenerated diagrams:", diagram_files)
    else:
        print("\nFailed to generate diagrams")

if __name__ == "__main__":
    main()