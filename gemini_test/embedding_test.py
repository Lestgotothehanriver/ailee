from google import genai
import os
from dotenv import load_dotenv

load_dotenv() 
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

#_______________________________________________________________________________________
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="Hello, world! This is a test for embedding content using Gemini AI."
)
print(result.embeddings)

#_______________________________________________________________________________________
result = client.models.embed_content(
        model="gemini-embedding-001",
        contents= [
            "What is the meaning of life?",
            "What is the purpose of existence?",
            "How do I bake a cake?"
        ])

for embedding in result.embeddings:
    print(embedding)
    
#_______________________________________________________________________________________

