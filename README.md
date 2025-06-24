# Notion Project Automation Bot

This project automates the generation and population of Notion pages for technical projects using AI (Gemini, Claude) and a PDF design document.

## Features
- Generates Notion pages for:
  - Background Information
  - Engineering Design (with text-based system architecture diagram)
  - Work Overview
  - Project Plan (8-week breakdown)
  - Daily Content (40 days)
- **Automatically generates a dataset if needed:**
  - If the project requires a dataset, the bot will generate a realistic CSV and extract only the headers for use in daily planning.
- Converts all Markdown headers and formatting to proper Notion blocks (no stray Markdown in Notion).
- All content is formatted for Notion (headers, paragraphs, etc.).

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up your `.env` file** in the project root with the following variables:
   ```env
   # Claude API key
   ANTHROPIC_API_KEY=your_claude_api_key_here

   # Gemini API key
   GOOGLE_API_KEY=your_gemini_api_key_here

   # Notion integration token
   NOTION_TOKEN=your_notion_integration_token_here

   # Notion parent page ID (where new project pages will be created)
   NOTION_PARENT_PAGE_ID=your_notion_parent_page_id_here
   ```
   - You can get your Notion integration token and parent page ID from the Notion developer portal and your workspace.
4. Run the bot:
   ```bash
   python bot.py
   ```
   - You can edit `bot.py` to specify which sections to generate and which PDF to use.

## System Architecture Images
- The engineering design section generates a **text-based system architecture diagram** (in Markdown, Mermaid, or ASCII).
- **To get an image:**
  1. Copy the generated diagram text.
  2. Paste it into Claude (or another AI tool that supports diagram/image generation from text).
  3. Download or screenshot the resulting image if needed.

## Notes
- The bot automatically detects if a dataset is required and extracts only the headers for use in daily planning.
- All Notion formatting is handled automatically—no Markdown artifacts will appear in your Notion pages.
- You can comment/uncomment sections in `main()` in `bot.py` to control which pages are generated.

## Troubleshooting
- If you see Markdown headers (e.g., `##`, `###`, `####`) in Notion, make sure you are using the latest code, which converts all headers to Notion blocks.
- For any issues, check the console output for error messages.

---

**Enjoy automated, beautifully formatted Notion project pages!** 