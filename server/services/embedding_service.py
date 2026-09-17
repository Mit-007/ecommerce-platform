from google import genai
from google.genai import types
from server.core.constant import EMBEDDING_MODEL,OUTPUT_DIMENSIONALITY
from server.core.logger import logger
from typing import Any
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

        return extract_embedding_vector(response)

    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")



def extract_embedding_vector(response: Any) -> list[float]:
    """
    Extract an embedding vector from an embedding model response.

    Returns:
        list[float]: The extracted embedding vector.

    Raises:
        ValueError: If no valid embedding vector is found.
        RuntimeError: If an unexpected error occurs during extraction.
    """

    # ============================================================
    # Method 1: response.embeddings[0].values
    # ============================================================
    try:
        if hasattr(response, "embeddings"):
            embeddings = response.embeddings

            if isinstance(embeddings, list) and embeddings:
                embedding = embeddings[0]

                if hasattr(embedding, "values"):
                    values = embedding.values

                    if values is not None:
                        vector = list(values)

                        if vector:
                            logger.debug(
                                "Embedding structure: response.embeddings[0].values"
                            )
                            return [float(value) for value in vector]

    except (IndexError, TypeError, AttributeError, ValueError):
        pass

    # ============================================================
    # Method 2: response.embeddings[0]["values"]
    # ============================================================
    try:
        if hasattr(response, "embeddings"):
            embeddings = response.embeddings

            if isinstance(embeddings, list) and embeddings:
                embedding = embeddings[0]

                if isinstance(embedding, dict) and "values" in embedding:
                    values = embedding["values"]

                    if values is not None:
                        vector = list(values)

                        if vector:
                            logger.debug(
                                "Embedding structure: response.embeddings[0]['values']"
                            )
                            return [float(value) for value in vector]

    except (IndexError, TypeError, ValueError, KeyError):
        pass

    # ============================================================
    # Method 3: response.embedding
    # ============================================================
    try:
        if hasattr(response, "embedding"):
            embedding = response.embedding

            if embedding is not None:
                vector = list(embedding)

                if vector:
                    logger.debug(
                        "Embedding structure: response.embedding"
                    )
                    return [float(value) for value in vector]

    except (TypeError, ValueError):
        pass

    # ============================================================
    # Method 4: response["embedding"]
    # ============================================================
    try:
        if isinstance(response, dict) and "embedding" in response:
            embedding = response["embedding"]

            if embedding is not None:
                vector = list(embedding)

                if vector:
                    logger.debug(
                        "Embedding structure: response['embedding']"
                    )
                    return [float(value) for value in vector]

    except (TypeError, ValueError, KeyError):
        pass

    # ============================================================
    # No valid embedding found
    # ============================================================
    logger.error(
        "Failed to extract embedding vector from response. "
        f"Response type: {type(response).__name__}"
    )

    raise ValueError(
        "Could not extract a valid embedding vector from the model response."
    )