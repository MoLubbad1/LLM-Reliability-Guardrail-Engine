# Auto-Guard: LLM Quality & Safety Pipeline

## Overview
Auto-Guard is a low-latency middleware service that acts as a secure buffer between a user and a main LLM. It automatically scores every interaction for safety and quality before the user ever sees the response. 

By implementing "LLM-as-a-Judge", this system uses one AI model to evaluate the output of another AI model, ensuring responses stick to safety policies and formatting rules.

## System Architecture
The pipeline operates on a multi-stage validation flow:

**Input Guardrails (Pre-processing):** A fast "Input Judge" scans the user's prompt for PII or prompt injection attempts. If flagged, the request is instantly blocked.
**Core Inference:** If the input is safe, it is passed to the main LLM (the "Worker") to generate a response.
**Output Guardrails (Post-processing):** An "Output Judge" evaluates the generated response against a strict rubric looking for hallucinations, toxicity, and schema compliance.
**Redis Caching:** To reduce latency and API token costs, a caching layer checks if the exact question has been asked before. If a user asks a repeated question, the middleware skips the LLM calls entirely and serves the pre-validated answer right away.

## Technology Stack
- **Framework:** FastAPI for serving the low-latency, asynchronous Python middleware API.
- **Caching:** Redis for production-scale latency management.
- **Validation:** Pydantic models to enforce structured JSON outputs from the LLM judges.
- **Models:** OpenAI API (`gpt-4o-mini`) used for cost-effective, high-speed reasoning and inference.
- **Testing:** Pytest and `pytest-asyncio` for adversarial benchmarking.

## Adversarial Testing (Red Teaming)
This repository includes a golden dataset built as an automated test suite to red team the API and prove the guardrails are effective. 

The automated test suite verifies that the system successfully:
* Catches and blocks PII.
* Catches and blocks Prompt Injection attempts.
* Catches and blocks toxic LLM responses.
* Saves and instantly retrieves validated AI responses from the Redis cache.

## Local Setup & Installation
1. Clone the repository and navigate into the project folder.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
3. Install the dependencies:

  ```bash
  pip install fastapi uvicorn pydantic openai redis pytest pytest-asyncio
  Start your local Redis server (Requires Homebrew on macOS):

  brew services start redis
  Export your OpenAI API Key:

  export OPENAI_API_KEY="sk-your-secret-key"
```
4. Boot the FastAPI Server:
```bash
uvicorn app.main:app --reload
View the interactive dashboard by navigating to http://127.0.0.1:8000/docs in your browser.
