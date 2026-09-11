from typing import Any
from app.core.logger import logger


def extract_response_text(response: Any) -> str:
    # ============================================================
    # Method 1: response.content[0]["text"]
    # ============================================================
    try:
        if hasattr(response, "content") and isinstance(response.content, list):
            if len(response.content) > 0:
                content_item = response.content[0]
                
                # Check if it's a dict with "text" key
                if isinstance(content_item, dict) and "text" in content_item:
                    text = content_item["text"]
                    if text is not None:
                        logger.debug("Response structure: response.content[0]['text']")
                        return str(text)
    
    except (IndexError, TypeError, AttributeError, KeyError):
        pass
    
    # ============================================================
    # Method 2: response.content[0].text
    # ============================================================
    try:
        if hasattr(response, "content") and isinstance(response.content, list):
            if len(response.content) > 0:
                content_item = response.content[0]
                
                # Check if it's an object with .text attribute
                if hasattr(content_item, "text"):
                    text = content_item.text
                    if text is not None:
                        logger.debug("Response structure: response.content[0].text")
                        return str(text)
    
    except (IndexError, TypeError, AttributeError):
        pass
    
    # ============================================================
    # Method 3: response.content (direct string or list)
    # ============================================================
    try:
        if hasattr(response, "content"):
            content = response.content
            
            # Check if it's directly a string
            if isinstance(content, str) and content is not None:
                logger.debug("Response structure: response.content (direct string)")
                return content
            
            # If it's a list with a single string item
            if isinstance(content, list) and len(content) > 0:
                if isinstance(content[0], str) and content[0] is not None:
                    logger.debug("Response structure: response.content[0] (string from list)")
                    return content[0]
    
    except (TypeError, AttributeError):
        pass
    
    # ============================================================
    # Method 4: response.text (alternative attribute)
    # ============================================================
    try:
        if hasattr(response, "text"):
            text = response.text
            if text is not None and isinstance(text, str):
                logger.debug("Response structure: response.text")
                return text
    
    except (TypeError, AttributeError):
        pass
    
    # ============================================================
    # Method 5: response.choices[0].message.content (OpenAI/Anthropic API)
    # ============================================================
    try:
        if hasattr(response, "choices") and isinstance(response.choices, list):
            if len(response.choices) > 0:
                choice = response.choices[0]
                
                # Check for .message.content pattern
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    text = choice.message.content
                    if text is not None:
                        logger.debug("Response structure: response.choices[0].message.content")
                        return str(text)
    
    except (IndexError, TypeError, AttributeError):
        pass
    
    # ============================================================
    # Method 6: response.choices[0]["message"]["content"] (dict variant)
    # ============================================================
    try:
        if hasattr(response, "choices") and isinstance(response.choices, list):
            if len(response.choices) > 0:
                choice = response.choices[0]
                
                if isinstance(choice, dict) and "message" in choice:
                    message = choice["message"]
                    if isinstance(message, dict) and "content" in message:
                        text = message["content"]
                        if text is not None:
                            logger.debug("Response structure: response.choices[0]['message']['content']")
                            return str(text)
    
    except (IndexError, TypeError, AttributeError, KeyError):
        pass
    
    # ============================================================
    # Method 7: Ultimate fallback (str conversion)
    # ============================================================
    try:
        result = str(response)
        if result and result != "None":
            logger.warning("Response structure: Using fallback str(response) conversion")
            return result
    
    except Exception as e:
        logger.error(f"Failed to extract response text: {str(e)}")
        return f"[Error extracting response: {str(e)}]"


from typing import Any
from app.core.logger import logger


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