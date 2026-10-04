"""
Embedding model utility module using SentenceTransformers.
Loads the 'all-MiniLM-L6-V2' model to convert input text lists into dense numerical vector representations.
Provides helper function get_embeddings() for vector store indexing and semantic query retrieval.
"""
_model = None

def get_model():
    global _model
    if _model is None:
        import torch
        # Optimize memory usage on constrained instances (e.g. Render Free Tier)
        torch.set_num_threads(1)
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_embeddings(texts):
    model = get_model()
    return model.encode(texts).tolist()
     