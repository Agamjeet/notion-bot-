import anthropic
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize clients
claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def read_pdf(file_path):
    """Read and extract text from PDF file"""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def generate_background():
    """Generate background information using Google AI Studio with PDF input"""
    try:
        # Read the design document from session state
        design_doc = read_pdf(st.session_state['pdf_path'])
        
        # Initialize Google AI model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Using this design document as reference:
        {design_doc}
        
        Generate a comprehensive background section for a hospital stay length prediction project. 
        Include information about:
        1. The importance of predicting hospital stay length
        2. Current challenges in healthcare resource management
        3. How AI can help in this domain
        Keep it professional and informative."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in generate_background: {str(e)}")
        return "Error generating background content"

def generate_engineering():
    """Generate engineering design using Claude with PDF input"""
    try:
        # Read the design document from session state
        design_doc = read_pdf(st.session_state['pdf_path'])
        
        prompt = f"""Using this design document as reference:
        {design_doc}
        
        Create a detailed engineering design section for a hospital stay length prediction system.
        Include:
        1. System architecture
        2. Data pipeline
        3. Model selection criteria
        4. Evaluation metrics
        Focus on technical details and best practices."""
        
        message = claude_client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error in generate_engineering: {str(e)}")
        return "Error generating engineering content"

def generate_work_overview():
    """Generate work overview using Google AI Studio with PDF input"""
    try:
        # Read the design document from session state
        design_doc = read_pdf(st.session_state['pdf_path'])
        
        # Initialize Google AI model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Using this design document as reference:
        {design_doc}
        
        Write a work overview section for a hospital stay length prediction project.
        Include:
        1. Project objectives
        2. Key deliverables
        3. Team structure
        4. Timeline overview
        Make it clear and actionable."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in generate_work_overview: {str(e)}")
        return "Error generating work overview content"

def generate_project_plan():
    """Generate project plan using Google AI Studio"""
    try:
        # Initialize Google AI model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """Create a high-level project plan for an 8-week hospital stay length prediction project.
        Include:
        1. Major milestones
        2. Key activities
        3. Resource requirements
        4. Risk management
        Structure it in a clear, timeline format."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in generate_project_plan: {str(e)}")
        return "Error generating project plan content"

def generate_daily_content(day):
    """Generate daily content using Google AI Studio"""
    try:
        # Initialize Google AI model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Create a detailed plan for Day {day} of the hospital stay length prediction project.
        Include:
        1. Specific tasks and objectives
        2. Required resources
        3. Expected outcomes
        4. Dependencies and blockers
        Make it specific and actionable for day {day}."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in generate_daily_content: {str(e)}")
        return f"Error generating content for day {day}" 