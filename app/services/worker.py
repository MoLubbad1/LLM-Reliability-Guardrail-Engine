import os
from openai import AsyncOpenAI

class WorkerLLM:
    """
    The core inference engine that generates responses for the user.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        # We use the same AsyncOpenAI client to prevent blocking the FastAPI server
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        self.system_prompt = (
            "You are a helpful, highly capable, and friendly AI assistant. "
            "Answer the user's questions clearly and accurately."
        )

    async def generate_response(self, user_prompt: str) -> str:
        """
        Takes the safe user prompt and generates an AI response.
        """
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7 # A slightly higher temperature for conversational variety
        )
        
        return response.choices[0].message.content