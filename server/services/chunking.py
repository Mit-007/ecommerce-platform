def create_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> list[str]:

    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks