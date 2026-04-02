from typing import List, Optional
import re

class BaseSplitter:
    def split_text(self, text: str) -> List[str]:
        raise NotImplementedError

class RecursiveCharacterSplitter(BaseSplitter):
    """
    Splits text by separators (double newline, single newline, sentences, space).
    Attempts to keep chunks below max_size while maintaining semantic integrity.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        final_chunks = []
        
        # Simple recursive logic to group characters
        # For brevity, we'll implement a clean version that splits by current separator
        def _recursive_split(current_text: str, separators: List[str]) -> List[str]:
            if not current_text:
                return []
            
            if len(current_text) <= self.chunk_size:
                return [current_text]
            
            if not separators:
                # Force split if no separators left
                return [current_text[i:i+self.chunk_size] for i in range(0, len(current_text), self.chunk_size - self.chunk_overlap)]

            sep = separators[0]
            remaining_seps = separators[1:]
            
            # Split by the first separator
            parts = current_text.split(sep)
            chunks = []
            current_chunk = ""
            
            for part in parts:
                if len(current_chunk) + len(part) + len(sep) <= self.chunk_size:
                    current_chunk += (sep if current_chunk else "") + part
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    # If the part itself is too big, split it recursively with next separator
                    if len(part) > self.chunk_size:
                        chunks.extend(_recursive_split(part, remaining_seps))
                        current_chunk = ""
                    else:
                        current_chunk = part
            
            if current_chunk:
                chunks.append(current_chunk)
            
            return chunks

        return _recursive_split(text, self.separators)

class SlidingWindowSplitter(BaseSplitter):
    """
    Splits text into fixed size chunks with a specified overlap.
    Simple and predictable.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += self.chunk_size - self.chunk_overlap
        
        return chunks

def get_splitter(strategy: str, **kwargs):
    if strategy == "recursive":
        return RecursiveCharacterSplitter(**kwargs)
    elif strategy == "sliding_window" or strategy == "simple":
        return SlidingWindowSplitter(**kwargs)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
