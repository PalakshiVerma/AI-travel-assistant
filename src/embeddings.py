"""
Embedding model utility module using SentenceTransformers.
Loads the 'all-MiniLM-L6-V2' model to convert input text lists into dense numerical vector representations.
Provides helper function get_embeddings() for vector store indexing and semantic query retrieval.
"""
from sentence_transformers import SentenceTransformer

model=SentenceTransformer('all-MiniLM-L6-V2')

def get_embeddings(texts):
    return model.encode(texts).tolist()
     