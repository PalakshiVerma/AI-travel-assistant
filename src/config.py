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

# Model provider: 'huggingface' or 'openai'
MODEL_PROVIDER = "huggingface"
FASTAPI_URL = "http://localhost:8000"