import re
from typing import List

# /c:/Users/Dell/Downloads/Multimodel_RAG/services/chunker.py
"""
Adaptive text chunking utility.

- Splits text into sentence-aware chunks with word-overlap.
- chunk_size and overlap are expressed in words and can be adjusted at runtime.
- Long sentences (longer than chunk_size) are further split by words.
"""



def _split_sentences(text: str) -> List[str]:
    """
    Naive sentence splitter that keeps sentence endings.
    Falls back to whole text if no sentence breaks found.
    """
    text = text.strip()
    if not text:
        return []
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[\.\?\!])\s+', text)
    # If split produced only one element, attempt to split on newlines
    if len(sentences) == 1 and "\n" in text:
        sentences = [s.strip() for s in text.splitlines() if s.strip()]
    return [s.strip() for s in sentences if s.strip()]


def _words(text: str) -> List[str]:
    return text.split()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100, min_chunk_size: int = 10) -> List[str]:
    """
    Break `text` into overlapping, sentence-aware chunks.

    Parameters:
    - text: input string to chunk.
    - chunk_size: target chunk size in words (default 500).
    - overlap: number of words to overlap between consecutive chunks (default 100).
    - min_chunk_size: minimum allowed chunk size (words) to avoid pathological values.

    Returns:
    - list of chunk strings.
    """
    if chunk_size <= 0 or overlap < 0:
        raise ValueError("chunk_size must be > 0 and overlap must be >= 0")
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    if chunk_size < min_chunk_size:
        raise ValueError(f"chunk_size must be at least {min_chunk_size} words")

    sentences = _split_sentences(text)
    chunks: List[str] = []
    current_sentences: List[str] = []
    current_word_count = 0

    for sent in sentences:
        sent_words = _words(sent)
        # If a single sentence is longer than chunk_size, split by words
        if len(sent_words) > chunk_size:
            # First, flush any existing current_sentences
            if current_sentences:
                chunk = " ".join(current_sentences).strip()
                if chunk:
                    chunks.append(chunk)
                # prepare overlap for next chunk
                overlap_words = _words(chunk)[-overlap:] if overlap > 0 else []
                current_sentences = [" ".join(overlap_words)] if overlap_words else []
                current_word_count = len(overlap_words)
            # Now split the long sentence into word-based subchunks
            step = chunk_size - overlap
            if step <= 0:
                step = chunk_size
            for i in range(0, len(sent_words), step):
                part = " ".join(sent_words[i:i + chunk_size]).strip()
                if part:
                    chunks.append(part)
            # reset current buffer
            current_sentences = []
            current_word_count = 0
            continue

        # Normal sentence fits within chunk_size
        if current_word_count + len(sent_words) <= chunk_size:
            current_sentences.append(sent)
            current_word_count += len(sent_words)
        else:
            # finalize current chunk
            chunk = " ".join(current_sentences).strip()
            if chunk:
                chunks.append(chunk)
            # create overlap fragment to start next chunk
            overlap_words = _words(chunk)[-overlap:] if overlap > 0 else []
            current_sentences = [" ".join(overlap_words)] if overlap_words else []
            current_word_count = len(overlap_words)
            # now add the sentence (it should fit because we flushed)
            current_sentences.append(sent)
            current_word_count += len(sent_words)

    # append any remaining text
    if current_sentences:
        final_chunk = " ".join(current_sentences).strip()
        if final_chunk:
            chunks.append(final_chunk)

    return chunks


# expose for imports
__all__ = ["chunk_text"]


class Chunker:
    """Configurable chunker that wraps the function API."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def configure(self, *, chunk_size: int = None, overlap: int = None) -> None:
        if chunk_size is not None:
            self.chunk_size = chunk_size
        if overlap is not None:
            self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        return chunk_text(text, chunk_size=self.chunk_size, overlap=self.overlap)