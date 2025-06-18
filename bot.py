from notion_client import Client
import os
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

def main():
    try:
        # Check if PDF exists
        pdf_path = 'design_doc.pdf'
        if not os.path.exists(pdf_path):
            print("❌ Error: design_doc.pdf not found!")
            return

        print("🚀 Starting content generation and Notion update...")
        
        # Create main project page
        project_title = extract_title_from_pdf(pdf_path)
        print(f"📝 Creating main project page: {project_title}")
        main_page = create_page_with_content(parent_page_id, project_title, f"Project: {project_title}")
        
        # Generate and update background
        print("📄 Generating Background Information...")
        background_content = generate_background()
        create_page_with_content(main_page, "Background Information", background_content)
        print("✅ Background Information updated")
        
        # Generate and update engineering design
        print("📄 Generating Engineering Design...")
        engineering_content = generate_engineering()
        create_page_with_content(main_page, "Engineering Design", engineering_content)
        print("✅ Engineering Design updated")
        
        # Generate and update work overview
        print("📄 Generating Work Overview...")
        work_content = generate_work_overview()
        create_page_with_content(main_page, "Work Overview", work_content)
        print("✅ Work Overview updated")
        
        # Generate and update project plan
        print("📄 Generating Project Plan...")
        plan_content = generate_project_plan()
        plan_page = create_page_with_content(main_page, "Project Plan", plan_content)
        print("✅ Project Plan updated")
        
        # Generate and update all daily content
        print("📅 Generating daily content...")
        for day in range(1, 41):
            print(f"  Generating Day {day}...", end='\r')
            content = generate_daily_content(day)
            create_page_with_content(plan_page, f"Day {day}", content)
        print("\n✅ All daily content updated")
        
        print("🎉 All content has been generated and updated to Notion!")
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()