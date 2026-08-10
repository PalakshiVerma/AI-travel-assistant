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
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "travel_assistant-collection")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Model provider: 'huggingface' or 'openai'
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "huggingface").strip().lower()
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")