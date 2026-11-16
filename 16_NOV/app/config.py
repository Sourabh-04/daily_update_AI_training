import os
from dotenv import load_dotenv

# Read the .env file and put its values into os.environ
load_dotenv()

# --- LLM settings ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "goedel").lower()   # "goedel" or "ollama"

GOEDEL_API_KEY = os.getenv("GOEDEL_API_KEY", "")
GOEDEL_BASE_URL = os.getenv("GOEDEL_BASE_URL", "https://api.goedelmachines.com/v1")
GOEDEL_MODEL = os.getenv("GOEDEL_MODEL", "deepseek/deepseek-v4.1-flash")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# --- Storage settings ---
SQLITE_PATH = os.getenv("SQLITE_PATH", "trips.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# .env values are always strings, so convert numbers with int()
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "86400"))   # 24 hours
SESSION_MAX_MESSAGES = int(os.getenv("SESSION_MAX_MESSAGES", "10"))
