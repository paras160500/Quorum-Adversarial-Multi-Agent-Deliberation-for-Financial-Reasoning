"""
LLM initialization for the Deep Thinking Trading System.

Both models use Ollama's OpenAI-compatible API. The model names, backend URL,
and API key are loaded from config.py.
"""

#============================================================================
#                                Import Statements
#============================================================================
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os 

load_dotenv()

from trading_agents.config import (
    BACKEND_URL,
    DEEP_THINK_LLM,
    OLLAMA_API_KEY,
    QUICK_THINK_LLM,
)

# Deep Thinking LLM
DEEP_THINKING_LLM = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.1,
)

# Quick Thinking LLM
QUICK_THINKING_LLM = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.1,
)

# Backwards Compatibility
deep_thinking_llm = DEEP_THINKING_LLM
quick_thinking_llm = QUICK_THINKING_LLM


def build_llms() -> tuple[ChatOpenAI, ChatOpenAI]:
    return deep_thinking_llm, quick_thinking_llm
