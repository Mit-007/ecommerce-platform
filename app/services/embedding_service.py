from google import genai
from google.genai import types
from app.core.constant import EMBEDDING_MODEL,OUTPUT_DIMENSIONALITY
from app.core.config import GOOGLE_API_KEY
from app.services.extract_response import extract_embedding_vector

try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize embedding service: {str(e)}")

def generate_embedding(text: str) -> list[float]:
    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=OUTPUT_DIMENSIONALITY,
            ),
        )

        return extract_embedding_vector(response)

    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")