"""
Central configuration for the Deep Thinking Trading System.

All configuration values are loaded directly from environment variables.
Create a .env file in the project root for local development.
"""

#============================================================================
#                                Import Statements
#============================================================================
import os
from dotenv import load_dotenv

load_dotenv()


# API Statements
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# LLM Statements
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

QUICK_THINK_LLM = os.getenv("QUICK_THINK_LLM", "qwen3:4b")
DEEP_THINK_LLM = os.getenv("DEEP_THINK_LLM", "llama3:latest")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434/v1",
)

BACKEND_URL = os.getenv("BACKEND_URL", OLLAMA_BASE_URL)
EMBEDDING_BACKEND_URL = os.getenv(
    "EMBEDDING_BACKEND_URL",
    OLLAMA_BASE_URL,
)

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama-local")


# LangSmith Statements
LANGSMITH_TRACING = os.getenv(
    "LANGSMITH_TRACING",
    "true" if LANGSMITH_API_KEY else "false",
).lower() in {"true", "1", "yes", "on"}

LANGSMITH_PROJECT = os.getenv(
    "LANGSMITH_PROJECT",
    "Standalone-TradingAgents-Live-Demo",
)


# Directory Statements
RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")
DATA_CACHE_DIR = os.getenv("DATA_CACHE_DIR", "./data_cache")


# Debate Statements
MAX_DEBATE_ROUNDS = int(os.getenv("MAX_DEBATE_ROUNDS", "2"))
MAX_RISK_DISCUSS_ROUNDS = int(
    os.getenv("MAX_RISK_DISCUSS_ROUNDS", "1")
)
MAX_RECUR_LIMIT = int(os.getenv("MAX_RECUR_LIMIT", "100"))


# Tool Statements
ONLINE_TOOLS = os.getenv(
    "ONLINE_TOOLS",
    "true",
).lower() in {"true", "1", "yes", "on"}


# Validation Statements
if not FINNHUB_API_KEY:
    raise ValueError("FINNHUB_API_KEY is not available")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not available")


# Directory Creation
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(DATA_CACHE_DIR, exist_ok=True)