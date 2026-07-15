from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.guardrails import GuardrailJudge
from app.services.worker import WorkerLLM
from app.core.cache import CacheService

app = FastAPI(title="Auto-Guard: LLM Quality & Safety Pipeline")

judge = GuardrailJudge(model_name="gpt-4o-mini")
worker = WorkerLLM(model_name="gpt-4o-mini")
cache = CacheService() # INITIALIZE CACHE

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # 0. Check the Cache First
    cached_data = await cache.get_cached_response(request.prompt)
    if cached_data:
        # Add a flag so you know it was cached during testing!
        cached_data["cached"] = True 
        return cached_data

    # 1. Pre-Processing 
    input_eval = await judge.evaluate_input(request.prompt)
    if not input_eval.is_safe:
        raise HTTPException(status_code=400, detail=f"Input blocked: {input_eval.reasoning}")

    # 2. Core Inference 
    worker_response = await worker.generate_response(request.prompt)

    # 3. Post-Processing
    output_eval = await judge.evaluate_output(request.prompt, worker_response)
    if not output_eval.is_safe:
        raise HTTPException(status_code=500, detail=f"Output blocked: {output_eval.reasoning}")

    # 4. Prepare Final Response
    final_response = {
        "status": "success",
        "worker_response": worker_response,
        "safety_score": output_eval.score,
        "evaluator_reasoning": output_eval.reasoning
    }

    # 5. Save to Cache for the next time
    await cache.set_cached_response(request.prompt, final_response)
    
    return final_response