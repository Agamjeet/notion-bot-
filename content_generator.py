import anthropic
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
import base64
import time
import random
import csv

# Load environment variables
load_dotenv()

# Initialize clients
claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def safe_generate_content(model, prompt, max_retries=3):
    """Safely generate content with retry logic for rate limiting"""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            if "429" in str(e) and "quota" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(1, 5)  # Exponential backoff
                    print(f"Rate limited, waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
                    continue
            raise e
    return None

def read_pdf(file_path):
    """Read and extract text from PDF file"""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def check_dataset_required(pdf_path):
    design_doc = read_pdf(pdf_path)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = (
        "Based on the following project design document, does the project require a dataset for its implementation? "
        "Answer only 'yes' or 'no'.\n\n"
        f"{design_doc}"
    )
    response = safe_generate_content(model, prompt)
    answer = response.text.strip().lower() if response else "no"
    return 'yes' in answer

def generate_background(pdf_path):
    """Generate background information using Google AI Studio with PDF input"""
    try:
        design_doc = read_pdf(pdf_path)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Using this design document as reference:
        {design_doc}
        
        Please write a "Background Information" section for this project, following the exact format and tone of the example provided below no bullet points only paragraphs.
        Your output must include:
        Introduction – Briefly describe what the system does and who it is for.
        Business Context and Core Challenges – Describe the real-world problems the system addresses. Focus on pain points that would motivate this solution (e.g., inefficiencies, manual processes, compliance challenges).
        System Overview and Objectives – Explain how the system works at a high level and what goals it aims to achieve.
        Core System Capabilities – Provide an illustrative end-to-end workflow (like a user adding data or generating a report) to demonstrate how the system handles key tasks, integrating both user actions and system behavior in a natural narrative.
        Intended Benefits – Clearly list the real-world value this system provides (e.g., automation, accuracy, client satisfaction, scalability).
        Write with a smooth, professional tone.
        Use this as your format and style reference:
        https://eggplant-gopher-290.notion.site/Background-Information-1e32195181708099a6c1fe2a52e8ecc8
        """
        response = safe_generate_content(model, prompt)
        return response.text
    except Exception as e:
        print(f"Error in generate_background: {str(e)}")
        return "Error generating background content"

def generate_engineering(pdf_path):
    """Generate engineering design as a text-based schema/diagram and explanations only, with Notion-friendly formatting."""
    try:
        design_doc = read_pdf(pdf_path)
        # Step 1: Get main components from Claude
        claude_prompt_components = f"""
From this project spec:
{design_doc}

List only the main system components for a system architecture diagram.
Do NOT explain them. Just give a short bullet-point summary like:
- Frontend (React)
- Backend (Flask API)
- PostgreSQL Database
- Auth0 (external auth service)
"""
        claude_components_response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": claude_prompt_components}]
        )
        components_list = claude_components_response.content[0].text.strip()

        diagram_prompt = f"""
Please generate a system architecture diagram for this project that is:
- Student-friendly: Keep all components and labels simple and easy to understand.
- Clearly connected: Show how each module (e.g., frontend, backend, database, APIs, external services) connects to others using clean, labeled arrows.
- Modular & Realistic: Include only core components necessary for the project's logic (e.g., UI → Backend → Database).
- Focused: Avoid clutter or unnecessary layers. Make it visually neat and explainable to a beginner-level engineer.
- Use readable font and simple shapes (rectangles for services, cylinders for databases, clouds for external APIs).

Here are the main components:
{components_list}

For each component, output the explanation as four separate lines:
- The first line should be the component name as a heading (e.g., ### Backend (Python Analytics Engine)).
- The next three lines should be full sentences, each starting with a label: Role:, Tools:, and Connection: (do NOT use Markdown bold or bullets, just plain text).
- Do NOT use bullet points or Markdown bold. Just output plain text so it can be parsed and formatted as Notion blocks.

Output the diagram as a Markdown code block (use Mermaid, ASCII, or clear indented text), then the explanations.
"""
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        diagram_response = safe_generate_content(gemini_model, diagram_prompt)
        diagram_description = diagram_response.text if diagram_response else "Architecture diagram description could not be generated."
        return {
            "schema": diagram_description,
            "component_explanations": ""
        }
    except Exception as e:
        print(f"Error in generate_engineering: {str(e)}")
        return {"error": str(e)}

def generate_work_overview(pdf_path):
    """Generate work overview using Google AI Studio with PDF input"""
    try:
        design_doc = read_pdf(pdf_path)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Using this design document as reference:
{design_doc}

Please write a Work Overview for this project using the same structure, tone, and length as the example provided below. The output must be structured as a technical yet readable document and include the following sections:
- Title – A clear, engaging, and technically accurate headline for the system.
- Abstract – One to two paragraphs summarizing the current industry problem and how the proposed system solves it. Focus on real-world relevance and technical innovation.
- 1. Introduction – Describe the broader context, real-world pain points, and why the system is needed. Include current limitations, inefficiencies, or gaps in typical workflows.
- 2. The Solution – Walk through the proposed system's user flow or end-to-end usage in a narrative, easy-to-follow format. Think like a product walkthrough from a user's perspective.
- 3. System Architecture and Technology – Describe key components and technical infrastructure. Include hardware, frameworks, models/libraries, core modules, and how data flows through the system. Be as specific and realistic as possible.
- 4. Key Features and Benefits – For this section, do NOT use Markdown tables. For each feature, use a heading (e.g., #### Feature Name). Under each heading, write two paragraphs: the first starts with 'Benefit for Real Estate Professionals / Investors:' in bold, followed by the benefit. The second starts with 'Benefit for Home Buyers & Sellers / Operators & Developers:' in bold, followed by the benefit. Do NOT use bullet points or lists, just headings and paragraphs. The output must be directly copy-pasteable into Notion and preserve all formatting.
- 5. Use Cases and Future Scope – Describe the primary intended setting, plus 2–3 realistic expansion ideas or alternate use cases.
- 6. Proof of Concept – Explain what has already been built or prototyped. Mention any visuals or video demonstrations if available (or describe how one would work).
- 7. Conclusion – Wrap up with a forward-looking summary, balancing excitement with realism. Mention remaining technical challenges (if applicable) and the project's long-term promise.
Important guidelines:
- Prioritize clarity, depth, and technical credibility.
- Output must be long-form, matching the tone and structure of this example:
https://eggplant-gopher-290.notion.site/Work-Overview-1e321951817080f29ec6e881c91e5a93
it is very important to follow same output of text that can be copied to notion
"""
        response = safe_generate_content(model, prompt)
        return response.text
    except Exception as e:
        print(f"Error in generate_work_overview: {str(e)}")
        return "Error generating work overview content"

def generate_project_plan():
    """Generate project plan using Google AI Studio"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """Create a high-level project plan for an 8-week h project.
        Include:
        1. Major milestones
        2. Key activities
        3. Resource requirements
        4. Risk management
        Structure it in a clear, timeline format.
        Please create an 8-week internship plan for this project. Each week should be presented as a short paragraph (not bullet points), written in simple, readable language suitable for a student-level intern.
        Guidelines:
        - Keep each paragraph to 7 lines or fewer.
        - Do not use bullet points, lists, or emojis.
        - Ensure the plan is progressive: earlier weeks should focus on setup and onboarding, while later weeks move toward implementation and final deliverables.
        - Each week's tasks should be logically connected to the next and tied to real, feasible components of the project (technical setup, data collection, model training, integration, testing, etc.).
        - Prioritize clarity, structure, and technical realism. Avoid fluff or generic language.

        """
        response = safe_generate_content(model, prompt)
        return response.text
    except Exception as e:
        print(f"Error in generate_project_plan: {str(e)}")
        return "Error generating project plan content"

def generate_daily_content(day, headers=None):
    """Generate daily content using Google AI Studio, referencing dataset headers if provided."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        if headers:
            prompt = (
                f"Create a detailed plan for Day {day} of the project.\n"
                f"The dataset for this project has the following columns: {headers}.\n"
                "If any tasks involve data, reference the relevant columns by name.\n"
                "Include:\n"
                "1. Specific tasks and objectives\n"
                "2. Required resources\n"
                "3. Expected outcomes\n"
                "4. Dependencies and blockers\n"
                f"Make it specific and actionable for day {day}."
            )
        else:
            prompt = (
                f"Create a detailed plan for Day {day} of the project. "
                "Include:\n"
                "1. Specific tasks and objectives\n"
                "2. Required resources\n"
                "3. Expected outcomes\n"
                "4. Dependencies and blockers\n"
                f"Make it specific and actionable for day {day}."
            )
        response = safe_generate_content(model, prompt)
        return response.text if response else "Error generating daily content."
    except Exception as e:
        print(f"Error in generate_daily_content: {str(e)}")
        return f"Error generating content for day {day}"

def generate_dataset(pdf_path, output_csv_path="dataset.csv"):
    """Generate a realistic dataset in CSV format for the project, with at least 100 rows."""
    design_doc = read_pdf(pdf_path)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = (
        "Based on the following project design document, generate a realistic dataset in CSV format suitable for this project. "
        "First, define the column headers. Then, provide at least 100 rows of plausible, realistic data (not just a sample). "
        "Output only the CSV content, no explanations or markdown formatting.\n\n"
        f"{design_doc}"
    )
    response = safe_generate_content(model, prompt)
    csv_content = response.text.strip() if response else ""
    # Save to file
    with open(output_csv_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    print(f"Dataset saved to {output_csv_path}")
    return output_csv_path 