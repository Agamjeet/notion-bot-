import streamlit as st
import tempfile
import os
from notion_client import Client
from dotenv import load_dotenv
from content_generator import (
    generate_background,
    generate_engineering,
    generate_work_overview,
    generate_project_plan,
    generate_daily_content
)

# Load environment variables
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv('NOTION_TOKEN'))
parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')

def extract_title_from_pdf(filename):
    """Extract title from PDF filename by removing numbers and extension"""
    # Remove .pdf extension
    name = os.path.splitext(filename)[0]
    # Remove leading numbers and dots
    title = ''.join(c for c in name if not c.isdigit() and c != '.')
    # Remove leading/trailing spaces and dots
    title = title.strip('. ')
    return title

def create_page_with_content(parent_id, title, content):
    """Create a page with title and content"""
    page = notion.pages.create(
        parent={"page_id": parent_id},
        properties={
            "title": [{"type": "text", "text": {"content": title}}]
        }
    )
    
    # Add content to the page
    notion.blocks.children.append(
        block_id=page["id"],
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }
        ]
    )
    return page["id"]

# Set page config
st.set_page_config(
    page_title="Content Generator",
    page_icon="📝",
    layout="wide"
)

# Custom CSS for better button styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .main-button {
        background-color: #2196F3 !important;
        font-size: 1.2em !important;
        padding: 15px !important;
    }
    .main-button:hover {
        background-color: #1976D2 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("📝 Content Generator")

# Sidebar for PDF upload
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state['pdf_path'] = tmp_file.name
            st.session_state['pdf_title'] = extract_title_from_pdf(uploaded_file.name)
        st.success("PDF uploaded successfully!")

# Main content area
if 'pdf_path' not in st.session_state:
    st.warning("Please upload a PDF file in the sidebar to begin.")
else:
    # Single button to generate and update everything
    if st.button("Generate and Update Everything to Notion", key="generate_all", help="Generate all content and update to Notion"):
        with st.spinner("Generating and updating content..."):
            try:
                # Create main project page
                project_title = st.session_state['pdf_title']
                main_page = create_page_with_content(parent_page_id, project_title, f"Project: {project_title}")
                
                # Generate and update background
                background_content = generate_background()
                create_page_with_content(main_page, "Background Information", background_content)
                st.success("✅ Background Information updated")
                
                # Generate and update engineering design
                engineering_content = generate_engineering()
                create_page_with_content(main_page, "Engineering Design", engineering_content)
                st.success("✅ Engineering Design updated")
                
                # Generate and update work overview
                work_content = generate_work_overview()
                create_page_with_content(main_page, "Work Overview", work_content)
                st.success("✅ Work Overview updated")
                
                # Generate and update project plan
                plan_content = generate_project_plan()
                plan_page = create_page_with_content(main_page, "Project Plan", plan_content)
                st.success("✅ Project Plan updated")
                
                # Generate and update all daily content
                st.info("Generating daily content...")
                progress_bar = st.progress(0)
                for day in range(1, 41):
                    content = generate_daily_content(day)
                    create_page_with_content(plan_page, f"Day {day}", content)
                    progress_bar.progress(day / 40)
                st.success("✅ All daily content updated")
                
                st.success("🎉 All content has been generated and updated to Notion!")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Cleanup function
def cleanup():
    if 'pdf_path' in st.session_state:
        try:
            os.unlink(st.session_state['pdf_path'])
        except:
            pass

# Add cleanup to session state
if 'cleanup_done' not in st.session_state:
    st.session_state['cleanup_done'] = False

# Run cleanup when the app is closed
if not st.session_state['cleanup_done']:
    cleanup()
    st.session_state['cleanup_done'] = True 