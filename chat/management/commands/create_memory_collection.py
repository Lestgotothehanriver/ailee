from django.core.management.base import BaseCommand
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams

class Command(BaseCommand):
    help = "Create Qdrant collection for chat messages"

    def handle(self, *args, **kwargs):
        client = QdrantClient(host="localhost", port=6333)
        client.recreate_collection(
            collection_name="chat_memory",
            vectors_config=VectorParams(
                size=768, #The size of the embedding vector based on gemini-embedding-001
                distance="Cosine"
            )
        )
        self.stdout.write(self.style.SUCCESS('Successfully created Qdrant collection for chat messages.'))