import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Suno Credentials
SUNO_EMAIL = os.getenv("SUNO_EMAIL")
SUNO_PASSWORD = os.getenv("SUNO_PASSWORD")

# Meus Dividendos Credentials
MEUS_DIVIDENDOS_EMAIL = os.getenv("MEUS_DIVIDENDOS_EMAIL")
MEUS_DIVIDENDOS_PASSWORD = os.getenv("MEUS_DIVIDENDOS_PASSWORD")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_PUBLIC = os.path.join(BASE_DIR, "downloads-publico")
DOWNLOADS_PRIVATE = os.path.join(BASE_DIR, "downloads-privado")
