"""
Embedding model utility module.
Uses Google Generative AI embeddings to avoid memory limits on Render Free Tier.
"""
from src.config import GEMINI_API_KEY

_model = None

def get_model():
    global _model
    if _model is None:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        _model = GoogleGenerativeAIEmbeddings(
            model="text-embedding-004",
            google_api_key=GEMINI_API_KEY
        )
    return _model

def get_embeddings(texts):
    model = get_model()
    return model.embed_documents(texts)
     