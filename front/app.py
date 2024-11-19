import streamlit as st
import requests
import json

st.set_page_config(page_title="Product Description", layout="wide")

st.title("Product Description")

# Create form
with st.form("architecture_form"):
    # Left column
    col1, col2 = st.columns(2)
    
    with col1:
        client_profile = st.text_area(
            "Client Profile",
            height=150,
            placeholder="Describe the client's business, industry, and specific needs..."
        )
        
        competitive_analysis = st.text_area(
            "Competitive Analysis",
            height=150,
            placeholder="Outline key competitors and market analysis..."
        )
        
        generated_hypotheses = st.text_area(
            "Generated Hypotheses",
            height=150,
            placeholder="List potential solutions and approaches..."
        )
        
        recommended_solution = st.text_area(
            "Recommended Solution",
            height=150,
            placeholder="Describe the proposed solution..."
        )
    
    with col2:
        technical_requirements = st.text_area(
            "Technical Requirements",
            height=150,
            placeholder="List technical specifications and requirements..."
        )
        
        client_feedback = st.text_area(
            "Feedback from Client",
            height=150,
            placeholder="Include any client feedback or concerns..."
        )
        
        next_steps = st.text_area(
            "Next Steps",
            height=150,
            placeholder="Outline the proposed next steps..."
        )

        notes = st.text_area(
            "Notes",
            height=150,
            placeholder="Additional notes and comments..."
        )

    submit_button = st.form_submit_button("Generate Architecture")

if submit_button:
    # Prepare the project description
    project_description = f"""
    Client Profile:
    {client_profile}

    Competitive Analysis:
    {competitive_analysis}

    Generated Hypotheses:
    {generated_hypotheses}

    Recommended Solution:
    {recommended_solution}

    Technical Requirements:
    {technical_requirements}

    Client Feedback:
    {client_feedback}

    Next Steps:
    {next_steps}

    Notes:
    {notes}
    """

    # Send request to FastAPI endpoint
    try:
        response = requests.post(
            "http://localhost:8000/v1/generate-architecture",
            json={"project_description": project_description}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            st.success("Architecture generated successfully!")
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["Deployment", "Testing", "Research"])
            
            with tab1:
                st.markdown("### Deployment Architecture")
                st.write(result["deployment"]["solution"])
                
            with tab2:
                st.markdown("### Testing Architecture")
                st.write(result["testing"]["solution"])
                
            with tab3:
                st.markdown("### Research Architecture")
                st.write(result["research"]["solution"])
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        st.error(f"Failed to connect to the server: {str(e)}")