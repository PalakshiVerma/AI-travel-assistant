"""
Configuration module for application settings and environment variables.
Loads API keys, Qdrant cluster host settings, collection names, and model configuration options.
Configures default embedding model and LLM provider choice (HuggingFace or OpenAI).
"""
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Model provider: 'huggingface', 'openai', or 'gemini'
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "gemini")
FASTAPI_URL = "http://localhost:8000"