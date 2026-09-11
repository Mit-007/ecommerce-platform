from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.constant import CHUNK_OVERLAP,CHUNK_SIZE

def create_chunks(text: str) -> list[str]:
    try:
        if not text:
            return []

        if CHUNK_OVERLAP >= CHUNK_SIZE:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        chunks = splitter.split_text(text)

        return chunks

    except ValueError:
        raise

    except Exception as e:
        raise RuntimeError(f"Failed to create text chunks: {e}") from e