import os
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

# Configure OpenAI and Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-pro')

class RAGQuery(BaseModel):
    query: str
    user_id: str
    chat_id: str
    book_id: Optional[str] = None

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict]
    query: str

class SelectedTextQuery(BaseModel):
    query: str
    selected_text: str
    user_id: str
    chat_id: str

class RAGService:
    def __init__(self):
        
        self.openai_client = openai_client
        self.gemini_model = gemini_model

    async def query_knowledge_base(self, query: str, book_id: str = None, limit: int = 5) -> List[Dict]:
        """
        Query the knowledge base using vector search
        """
        # Perform semantic search in Qdrant
        search_results = self.qdrant_manager.search_similar_texts(query, limit=limit)

        # Filter by book_id if specified
        if book_id:
            search_results = [result for result in search_results if result.get('book_id') == book_id]

        return search_results

    async def generate_response(self, query: str, context: List[Dict]) -> str:
        """
        Generate a response using OpenAI as primary and Gemini as fallback based on the query and context
        """
        # Prepare context for the model
        context_texts = [item['text'] for item in context]
        context_str = "\n\n".join(context_texts)

        # Create a prompt for the model
        prompt = f"""
        You are a helpful assistant that answers questions based on provided context.
        Use only the information provided in the context to answer the question.
        If the answer cannot be found in the context, say "I don't have enough information in the provided context to answer this question."

        Context:
        {context_str}

        Question: {query}

        Answer:
        """

        # Try OpenAI first
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response with OpenAI: {e}")
            print("Falling back to Gemini...")

            # Fallback to Gemini
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.gemini_model.generate_content(prompt)
                )
                return response.text if response.text else "I couldn't generate a response based on the provided context."
            except Exception as e2:
                print(f"Error generating response with Gemini: {e2}")
                return "Sorry, I encountered an error while generating the response."

    async def generate_response_from_selected_text(self, query: str, selected_text: str) -> str:
        """
        Generate a response using only the selected text with OpenAI as primary and Gemini as fallback
        """
        # Create a prompt for the model using only selected text
        prompt = f"""
        You are a helpful assistant that answers questions based only on the provided selected text.
        Use only the information provided in the selected text to answer the question.
        If the answer cannot be found in the selected text, say "I don't have enough information in the selected text to answer this question."

        Selected Text:
        {selected_text}

        Question: {query}

        Answer:
        """

        # Try OpenAI first
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based only on the provided selected text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response with OpenAI: {e}")
            print("Falling back to Gemini...")

            # Fallback to Gemini
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.gemini_model.generate_content(prompt)
                )
                return response.text if response.text else "I couldn't generate a response based on the selected text."
            except Exception as e2:
                print(f"Error generating response from selected text with Gemini: {e2}")
                return "Sorry, I encountered an error while generating the response from selected text."

    async def process_rag_query(self, query: str, book_id: str = None) -> RAGResponse:
        """
        Process a RAG query and return the response
        """
        # Search for relevant documents
        context = await self.query_knowledge_base(query, book_id)

        # Generate response based on context
        answer = await self.generate_response(query, context)

        return RAGResponse(
            answer=answer,
            sources=context,
            query=query
        )

    async def process_selected_text_query(self, query: str, selected_text: str) -> RAGResponse:
        """
        Process a query against selected text only
        """
        # Generate response based only on selected text
        answer = await self.generate_response_from_selected_text(query, selected_text)

        # For selected text queries, sources would be the selected text itself
        sources = [{
            "text": selected_text,
            "source": "user_selected_text",
            "score": 1.0
        }]

        return RAGResponse(
            answer=answer,
            sources=sources,
            query=query
        )

# Global instance
rag_service = RAGService()