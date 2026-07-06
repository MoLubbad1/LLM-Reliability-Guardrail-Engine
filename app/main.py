from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.guardrails import GuardrailJudge
from app.services.worker import WorkerLLM

# Initialize the FastAPI app
app = FastAPI(title="Auto-Guard: LLM Quality & Safety Pipeline")

# Initialize your Judge Engine
judge = GuardrailJudge(model_name="gpt-4o-mini")
worker = WorkerLLM(model_name="gpt-4o-mini")

# Schema for the incoming user request
class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Middleware endpoint that automatically scores interactions for safety and quality.
    """
    # 1. Pre-Processing (Input Guardrails)
    input_eval = await judge.evaluate_input(request.prompt)
    
    if not input_eval.is_safe:
        # If the returned schema flags is_safe: False, block the request instantly.
        # Future step: Log this failure mode to a database.
        raise HTTPException(
            status_code=400, 
            detail=f"Input blocked by Auto-Guard: {input_eval.reasoning}"
        )

    # 2. Core Inference (The "Worker")
    worker_response = await worker.generate_response(request.prompt)

    # 3. Post-Processing (Output Guardrails)
    output_eval = await judge.evaluate_output(request.prompt, worker_response)
    
    if not output_eval.is_safe:
        # If the output violates quality/safety, block it before the user sees it.
        # Future step: Trigger a "Refinement Prompt" instead of just failing.
        raise HTTPException(
            status_code=500, 
            detail=f"Output blocked by Auto-Guard: {output_eval.reasoning}"
        )

    # 4. Final Return
    return {
        "status": "success",
        "worker_response": worker_response,
        "safety_score": output_eval.score,
        "evaluator_reasoning": output_eval.reasoning
    }