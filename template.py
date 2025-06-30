from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define your project name and base path
PROJECT_NAME = "bizintel"
CURRENT_DIR = Path.cwd()

# If already inside `bizintel`, use it as base
if CURRENT_DIR.name.lower() == PROJECT_NAME.lower():
    BASE_DIR = CURRENT_DIR
else:
    BASE_DIR = CURRENT_DIR / PROJECT_NAME
    BASE_DIR.mkdir(exist_ok=True)

# Define folder structure
folders = [
    "app/routes",
    "app/agents",
    "backend",
    "llm",
    "data/raw",
    "data/processed",
    "data/user_data",
    "streamlit_ui/components",
    "streamlit_ui/assets",
    "api_docs",
    "tests"
]

# Define starter files
files = [
    "app/__init__.py",
    "app/main.py",
    "app/routes/__init__.py",
    "app/routes/ingest.py",
    "app/routes/summarize.py",
    "app/routes/user.py",
    "app/agents/__init__.py",
    "app/agents/agent_registry.py",
    "backend/auth.py",
    "backend/database.py",
    "backend/models.py",
    "backend/scheduler.py",
    "llm/summarizer.py",
    "llm/retriever.py",
    "llm/prompts.py",
    "streamlit_ui/dashboard.py",
    "streamlit_ui/components/charts.py",
    "streamlit_ui/components/sidebar.py",
    "streamlit_ui/components/insights.py",
    "api_docs/openapi_schema.json",
    "tests/test_agents.py",
    "tests/test_llm.py",
    "tests/test_routes.py",
    ".env",
    "requirements.txt",
    "README.md",
    "run.sh"
]

def create_structure():
    for folder in folders:
        folder_path = BASE_DIR / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"📁 Created directory: {folder_path.relative_to(CURRENT_DIR)}")

    for file in files:
        file_path = BASE_DIR / file
        if not file_path.exists():
            file_path.touch()
            logging.info(f"📄 Created file: {file_path.relative_to(CURRENT_DIR)}")

    logging.info("✅ BizIntel project structure created successfully!")

if __name__ == "__main__":
    create_structure()
