import json
import os
import argparse
import sys
import plantuml
from swarm import Agent, Swarm
from dotenv import load_dotenv
load_dotenv()

class ArchitectureAgent:
    def __init__(self, output_dir="output"):
        self.swarm = Swarm()
        # Изменяем URL на более надежный сервер
        self.plantuml_server = plantuml.PlantUML(
            url="http://www.plantuml.com/plantuml/png/"
        )

        # Используем переданную директорию
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

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
            DO NOT wrap the response in markdown code blocks or ```json tags.""",
        )

    def generate_diagrams(self, architecture_description):
        messages = [
            {
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
        """,
            }
        ]

        try:
            response = self.swarm.run(agent=self.diagram_agent, messages=messages)

            raw_content = response.messages[-1]["content"]
            print("\n=== RAW RESPONSE START ===")
            print(raw_content)
            print("=== RAW RESPONSE END ===\n")

            cleaned_content = raw_content.strip()
            if cleaned_content.startswith("```"):
                cleaned_content = cleaned_content.split("\n", 1)[1]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content.rsplit("\n", 1)[0]
            if cleaned_content.startswith("json"):
                cleaned_content = cleaned_content.split("\n", 1)[1]

            diagrams = json.loads(cleaned_content)
            output_files = {}

            for diagram_type, puml_code in diagrams.items():
                # Используем self.output_dir вместо хардкода
                output_file = os.path.join(self.output_dir, f"{diagram_type}.png")
                print(f"\nProcessing {diagram_type}...")
                print(f"PlantUML code:\n{puml_code}\n")

                try:
                    # Добавляем обработку ошибок PlantUML
                    try:
                        png_data = self.plantuml_server.processes(puml_code)
                    except Exception as puml_error:
                        print(f"PlantUML Error: {str(puml_error)}")
                        print("Trying to fix PlantUML code...")
                        fixed_code = puml_code.replace("\n\n", "\n").strip()
                        png_data = self.plantuml_server.processes(fixed_code)

                    with open(output_file, "wb") as f:
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
    parser = argparse.ArgumentParser(description='Generate architecture diagrams from description')
    parser.add_argument('--output-dir', default='output',
                      help='Directory for output files (default: output)')
    args = parser.parse_args()

    architecture_description = sys.stdin.read()
    agent = ArchitectureAgent(output_dir=args.output_dir)
    diagram_files = agent.generate_diagrams(architecture_description)
    print(diagram_files)


if __name__ == "__main__":
    main()
