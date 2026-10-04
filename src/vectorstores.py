"""
Vector store management module for interacting with Qdrant database.
Provides client instantiation for Qdrant API connection and collection initialization utilities.
Ensures vector collections exist with proper dimensions and cosine similarity metrics upon application start.
"""
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from src.config import QDRANT_HOST, QDRANT_API_KEY, COLLECTION_NAME

def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_HOST,
        api_key=QDRANT_API_KEY
    )

def init_qdrant():
    # connect to qdrant cloud or local
    client = get_qdrant_client()
    try:
        # create collection if it doesn't exist
        existing_collections = [col.name for col in client.get_collections().collections]
        if COLLECTION_NAME not in existing_collections:
            print(f"Creating collection '{COLLECTION_NAME}'...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # SentenceTransformer all-MiniLM-L6-v2 embedding size
                    distance=Distance.COSINE,
                ),
            )
        print("Qdrant connection successful.")
    except Exception as e:
        print(f"WARNING: Could not connect to Qdrant on startup: {e}")
        print("WARNING: The server will start, but upload/query features may fail until Qdrant is reachable.")
    return client
