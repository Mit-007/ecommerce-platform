from google import genai
from google.genai import types
from server.core.constant import EMBEDDING_MODEL,OUTPUT_DIMENSIONALITY

from server.core.config import GOOGLE_API_KEY


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

        return response.embeddings[0].values

    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")