from django.core.management.base import BaseCommand
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams

class Command(BaseCommand):
    help = "Create Qdrant collection"

    size = 1536  # OpenAI text-embedding-3-small

    def handle(self, *args, **options):
        client = QdrantClient(host='localhost', port=6333)
        client.recreate_collection(
            collection_name="slab_vectors",
            vectors_config=VectorParams(
                size=size, 
                distance="Cosine"
            ))
        client.recreate_collection(
            collection_name="user_vectors",
            vectors_config=VectorParams(
                size=size, 
                distance="Cosine"
            ))
        self.stdout.write(self.style.SUCCESS('Successfully created Qdrant collections.'))
        