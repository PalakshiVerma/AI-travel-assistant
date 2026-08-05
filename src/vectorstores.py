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
    return client
