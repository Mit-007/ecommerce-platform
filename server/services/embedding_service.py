from google import genai
from google.genai import types

from server.core.config import GOOGLE_API_KEY


client = genai.Client(api_key=GOOGLE_API_KEY)


def generate_embedding(text: str) -> list[float]:
    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=1536,
            ),
        )

        return response.embeddings[0].values

    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")