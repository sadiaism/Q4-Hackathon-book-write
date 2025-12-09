import os
import asyncio
import json
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import qdrant_manager

load_dotenv()

class DocumentIngestor:
    """
    A class to handle document ingestion into Qdrant vector database
    """

    def __init__(self):
        self.qdrant_manager = qdrant_manager

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """
        Split text into overlapping chunks

        Args:
            text: The text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters

        Returns:
            List of dictionaries with chunk information
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            # If this is the last chunk, make sure we include all remaining text
            if end > text_length:
                end = text_length

            chunk_text = text[start:end]

            chunk_info = {
                "chunk_id": f"chunk_{start}_{end}",
                "text": chunk_text,
                "metadata": {
                    "start_pos": start,
                    "end_pos": end,
                    "chunk_size": len(chunk_text)
                }
            }

            chunks.append(chunk_info)

            # Move start position by chunk_size minus overlap
            start = end - overlap

            # If start position would exceed text length, break
            if start >= text_length:
                break

        return chunks

    async def ingest_from_file(self, file_path: str, book_id: str) -> bool:
        """
        Ingest content from a text file into Qdrant

        Args:
            file_path: Path to the text file
            book_id: Identifier for the book/document

        Returns:
            Success status
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Chunk the content
            chunks = self.chunk_text(content)

            # Add book_id to each chunk
            for chunk in chunks:
                chunk['book_id'] = book_id

            # Add chunks to Qdrant
            success = self.qdrant_manager.add_text_chunks(chunks, book_id)

            if success:
                print(f"Successfully ingested {len(chunks)} chunks from {file_path}")
                return True
            else:
                print(f"Failed to ingest chunks from {file_path}")
                return False

        except Exception as e:
            print(f"Error ingesting file {file_path}: {e}")
            return False

    async def ingest_from_text(self, text: str, book_id: str, source: str = "unknown") -> bool:
        """
        Ingest content from a text string into Qdrant

        Args:
            text: The text content to ingest
            book_id: Identifier for the book/document
            source: Source identifier for the text

        Returns:
            Success status
        """
        try:
            # Chunk the content
            chunks = self.chunk_text(text)

            # Add book_id and source to each chunk
            for chunk in chunks:
                chunk['book_id'] = book_id
                chunk['source'] = source

            # Add chunks to Qdrant
            success = self.qdrant_manager.add_text_chunks(chunks, book_id)

            if success:
                print(f"Successfully ingested {len(chunks)} chunks from text source: {source}")
                return True
            else:
                print(f"Failed to ingest chunks from text source: {source}")
                return False

        except Exception as e:
            print(f"Error ingesting text from source {source}: {e}")
            return False

    async def ingest_from_docusaurus_docs(self, docs_dir: str, book_id: str) -> bool:
        """
        Ingest content from Docusaurus documentation files

        Args:
            docs_dir: Directory containing Docusaurus markdown files
            book_id: Identifier for the book/document

        Returns:
            Success status
        """
        try:
            docs_path = Path(docs_dir)
            markdown_files = list(docs_path.rglob("*.md")) + list(docs_path.rglob("*.mdx"))

            total_chunks = 0
            for md_file in markdown_files:
                print(f"Processing file: {md_file}")

                with open(md_file, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Simple preprocessing to remove common markdown artifacts
                # Remove frontmatter if present
                if content.startswith('---'):
                    try:
                        end_frontmatter = content.find('---', 3)
                        if end_frontmatter != -1:
                            content = content[end_frontmatter + 3:]
                    except:
                        pass  # If frontmatter parsing fails, continue with original content

                # Chunk the content
                chunks = self.chunk_text(content)

                # Add book_id and source to each chunk
                for chunk in chunks:
                    chunk['book_id'] = book_id
                    chunk['source'] = str(md_file)

                # Add chunks to Qdrant
                success = self.qdrant_manager.add_text_chunks(chunks, book_id)

                if success:
                    total_chunks += len(chunks)
                    print(f"Successfully ingested {len(chunks)} chunks from {md_file}")
                else:
                    print(f"Failed to ingest chunks from {md_file}")
                    return False

            print(f"Successfully ingested {total_chunks} total chunks from Docusaurus docs")
            return True

        except Exception as e:
            print(f"Error ingesting Docusaurus docs from {docs_dir}: {e}")
            return False

# Example usage
async def main():
    """
    Example of how to use the DocumentIngestor
    """
    ingestor = DocumentIngestor()

    # Example 1: Ingest from a text file
    # await ingestor.ingest_from_file("path/to/your/book.txt", "my_book_1")

    # Example 2: Ingest from text content
    # sample_text = "This is a sample text that would come from your Docusaurus documentation..."
    # await ingestor.ingest_from_text(sample_text, "my_book_1", "sample_content")

    # Example 3: Ingest from Docusaurus docs directory
    # await ingestor.ingest_from_docusaurus_docs("./docs", "my_docusaurus_book")

if __name__ == "__main__":
    asyncio.run(main())