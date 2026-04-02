from openai import OpenAI
from app.core.config import settings
from app.services.vector_store import vector_store
from typing import List, Dict

class RAGService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )

    def generate_response(self, query: str, history: List[Dict[str, str]]) -> str:
        # 1. Search for context
        # We can also use rewritten query if history is long, but keeping it simple for now
        # Search the top 3 relevant chunks
        context_chunks = vector_store.search(query, limit=3)
        context = "\n\n".join([chunk.get("text", "") for chunk in context_chunks])
        
        # 2. Build the message context
        system_prompt = f"""
        You are a helpful AI assistant. Use the following pieces of retrieved context to answer the user's question.
        If the context doesn't contain the answer, say you don't know, but try to be as helpful as possible based on common knowledge.
        
        RETRIEVED CONTEXT:
        {context}
        """
        
        # 3. Assemble messages (History + Current Prompt)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add historical context (up to last 5 messages for token efficiency)
        messages.extend(history[-5:])
        
        # Add the current query
        messages.append({"role": "user", "content": query})
        
        # 4. Generate completions
        response = self.client.chat.completions.create(
            model="models/gemini-flash-latest",
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content

rag_service = RAGService()
