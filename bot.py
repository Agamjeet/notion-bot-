from notion_client import Client
import os
from dotenv import load_dotenv
from content_generator import (
    generate_background,
    generate_engineering,
    generate_work_overview,
    generate_project_plan,
    generate_daily_content,
    check_dataset_required,
    generate_dataset,
)
import re

# Load environment variables
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv('NOTION_TOKEN'))
parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')

def extract_title_from_pdf(filename):
    """Extract title from PDF filename: take everything after the first number and nothing before."""
    # Get just the filename, not the full path
    name = os.path.basename(filename)
    # Remove .pdf extension
    name = os.path.splitext(name)[0]
    match = re.search(r'\d', name)
    if match:
        # Take everything after the first digit
        title = name[match.end():].strip('. _-')
        # Clean up any remaining artifacts
        title = re.sub(r'^[0-9\s\._-]+', '', title)  # Remove leading numbers, dots, spaces, underscores
        return title.strip()
    else:
        return name

def split_text_blocks(text, max_length=2000):
    """Split text into chunks of max_length, breaking at newlines if possible."""
    blocks = []
    while len(text) > max_length:
        split_at = text.rfind('\n', 0, max_length)
        if split_at == -1 or split_at < max_length // 2:
            split_at = max_length
        blocks.append(text[:split_at])
        text = text[split_at:]
    if text:
        blocks.append(text)
    return blocks

def markdown_to_notion_blocks(text):
    blocks = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('#### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[5:]}}]
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                }
            })
        elif line.startswith('# '):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        elif re.match(r'^\*\*[^*]+?\*\*$', line):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:-2]}}]
                }
            })
        elif line:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })
    return blocks

def remove_markdown_bold_italic(text):
    # Remove all **bold** and *italic* markers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def create_page_with_content(parent_id, title, content, image_url=None, pdf_url=None, image_caption=None):
    """Create a page with title, content, and optionally images from Imgur URLs."""
    page = notion.pages.create(
        parent={"page_id": parent_id},
        properties={
            "title": [{"type": "text", "text": {"content": title}}]
        }
    )
    children = []

    # Add image if provided
    if image_url:
        children.append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": image_url}
            }
        })
        if image_caption:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": image_caption}}]
                }
            })

    # Add PDF link if provided
    if pdf_url:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "📄 Design Document: "},
                        "annotations": {"bold": True}
                    },
                    {
                        "type": "text",
                        "text": {"content": "View PDF"},
                        "annotations": {"color": "blue"},
                        "href": pdf_url
                    }
                ]
            }
        })

    # Remove Markdown bold/italic before converting to Notion blocks
    content = remove_markdown_bold_italic(content)
    blocks = markdown_to_notion_blocks(content)
    children.extend(blocks)

    notion.blocks.children.append(
        block_id=page["id"],
        children=children
    )
    return page["id"]

def main():
    try:
        # Check if PDF exists
        pdf_path = r'C:\Users\padda\Downloads\prompt engineerin\10 projects\19.DABA_Real Estate price prediction (BB0019DABA003M).pdf'
        if not os.path.exists(pdf_path):
            print("❌ Error: design_doc.pdf not found!")
            return

        # print("🚀 Starting content generation and Notion update...")
        
        # # Step 0: Check if dataset is required and get headers if needed
        # dataset_headers = None
        # if check_dataset_required(pdf_path):
        #     print("Yes, dataset is required.")
        #     csv_path = generate_dataset(pdf_path)
        #     with open(csv_path, 'r', encoding='utf-8') as f:
        #         dataset_headers = f.readline().strip()
        #     print("Dataset headers:", dataset_headers)
        # else:
        #     print("No, dataset is required.")
        
        # Create main project page
        project_title = extract_title_from_pdf(pdf_path)
        print(f"📝 Creating main project page: {project_title}")
        main_page = create_page_with_content(parent_page_id, project_title, f"Project: {project_title}")
        
        # # Generate and update background
        # print("📄 Generating Background Information...")
        # background_content = generate_background(pdf_path)
        # create_page_with_content(main_page, "Background Information", background_content)
        # print("✅ Background Information updated")
        
        # # Generate and update engineering design
        # print("📄 Generating Engineering Design...")
        # eng_result = generate_engineering(pdf_path)
        # if "error" in eng_result:
        #     print(f"❌ Error in engineering design: {eng_result['error']}")
        #     create_page_with_content(main_page, "Engineering Design", "Error generating engineering content")
        # else:
        #     eng_text = eng_result["schema"] + "\n\n" + eng_result["component_explanations"]
        #     create_page_with_content(
        #         main_page, 
        #         "Engineering Design", 
        #         eng_text
        #     )
        # print("✅ Engineering Design updated")
        
        # Generate and update work overview
        print("📄 Generating Work Overview...")
        work_content = generate_work_overview(pdf_path)
        create_page_with_content(main_page, "Work Overview", work_content)
        print("✅ Work Overview updated")
        
        # Generate and update project plan
        # print("📄 Generating Project Plan...")
        # plan_content = generate_project_plan()
        # plan_page = create_page_with_content(main_page, "Project Plan", plan_content)
        # print("✅ Project Plan updated")
        
        # Generate and update all daily content
        # print("📅 Generating daily content...")
        # for day in range(1, 41):
        #     print(f"  Generating Day {day}...", end='\r')
        #     content = generate_daily_content(day, headers=dataset_headers)
        #     create_page_with_content(plan_page, f"Day {day}", content)
        # print("\n✅ All daily content updated")
        
        # print("🎉 All content has been generated and updated to Notion!")
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()