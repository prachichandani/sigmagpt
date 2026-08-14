from typing import List, Dict, Optional
from core.config import CHUNK_SIZE, CHUNK_OVERLAP


SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]


def chunk_text(text: str, page_number: Optional[int] = None) -> List[Dict]:
    """
    Manual recursive separator-based chunking with word-aware overlap.

    Splits text using separators from coarse to fine:
    paragraph -> line -> sentence -> phrase -> word.

    Args:
        text: Input text to chunk.
        page_number: Optional page number for PDF documents.

    Returns:
        List of chunks with metadata.
    """
    if not text or not text.strip():
        return []

    if CHUNK_OVERLAP >= CHUNK_SIZE:
        raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

    text = normalize_text(text)

    chunks_data = recursive_split(text, SEPARATORS, CHUNK_SIZE)
    chunks_data = add_overlap(chunks_data, CHUNK_OVERLAP, CHUNK_SIZE)

    chunks = []

    for chunk in chunks_data:
        chunk = chunk.strip()

        if not chunk:
            continue

        chunks.append({
            "text": chunk,
            "page_number": page_number,
            "chunk_index": len(chunks),
            "chunk_type": "manual_recursive_separator",
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP
        })

    return chunks


def recursive_split(text: str, separators: List[str], chunk_size: int) -> List[str]:
    """
    Recursively split text using separators in order of preference.

    Args:
        text: Text to split.
        separators: Separators from coarse to fine.
        chunk_size: Maximum chunk size.

    Returns:
        List of text chunks.
    """
    text = text.strip()

    if len(text) <= chunk_size:
        return [text]

    if not separators:
        return split_by_character(text, chunk_size)

    separator = separators[0]
    splits = [s.strip() for s in text.split(separator) if s.strip()]

    if len(splits) == 1:
        return recursive_split(text, separators[1:], chunk_size)

    chunks = []
    current_chunk = ""

    for split in splits:
        piece = split if not current_chunk else separator + split

        if len(split) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            chunks.extend(recursive_split(split, separators[1:], chunk_size))

        elif len(current_chunk) + len(piece) <= chunk_size:
            current_chunk += piece

        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            current_chunk = split

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def add_overlap(chunks: List[str], overlap: int, chunk_size: int) -> List[str]:
    """
    Add word-aware overlap between chunks.

    Args:
        chunks: List of chunks.
        overlap: Number of characters to overlap.
        chunk_size: Maximum chunk size.

    Returns:
        List of chunks with overlap.
    """
    if not chunks or overlap <= 0:
        return chunks

    overlapped_chunks = [chunks[0]]

    for i in range(1, len(chunks)):
        previous = chunks[i - 1]
        current = chunks[i]

        overlap_text = get_word_overlap(previous, overlap)
        combined = f"{overlap_text} {current}".strip()

        if len(combined) > chunk_size:
            combined = trim_to_word_boundary(combined, chunk_size)

        overlapped_chunks.append(combined)

    return overlapped_chunks


def get_word_overlap(text: str, overlap: int) -> str:
    """
    Get overlap text without cutting the first word when possible.
    """
    text = text.strip()

    if len(text) <= overlap:
        return text

    overlap_part = text[-overlap:]
    first_space = overlap_part.find(" ")

    if first_space != -1:
        return overlap_part[first_space + 1:].strip()

    return overlap_part.strip()


def trim_to_word_boundary(text: str, max_size: int) -> str:
    """
    Trim text to max_size without cutting the last word when possible.
    """
    if len(text) <= max_size:
        return text

    trimmed = text[:max_size]
    last_space = trimmed.rfind(" ")

    if last_space != -1 and last_space > max_size // 2:
        return trimmed[:last_space].strip()

    return trimmed.strip()


def split_by_character(text: str, chunk_size: int) -> List[str]:
    """
    Split text by character as a last fallback.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end

    return chunks


def normalize_text(text: str) -> str:
    """
    Normalize text by removing empty lines and extra spaces.
    """
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)