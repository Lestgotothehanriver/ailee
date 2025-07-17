from qdrant_client import QdrantClient

qdrant = QdrantClient(host="localhost", port=6333)

#docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
