from groq import Groq
import json, os
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_requirements_agent(user_prompt, ledger):
    system_prompt = """You are a Requirements Agent. Convert a vague user idea into a structured JSON spec.
Return ONLY valid JSON with these fields:
{
  "project_name": "...",
  "description": "...",
  "api_endpoints": [{"method": "GET/POST", "path": "/...", "description": "..."}],
  "data_models": [{"name": "...", "fields": [...]}],
  "confidence_score": 0.0-1.0,
  "ambiguities": ["..."]
}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw = response.choices[0].message.content
    # Strip markdown if present
    raw = raw.strip().strip("```json").strip("```").strip()
    spec = json.loads(raw)

    ledger.log(
        agent="Requirements Agent",
        decision=f"Converted prompt to spec: {spec['project_name']}",
        reasoning=f"Identified {len(spec['api_endpoints'])} endpoints, confidence: {spec['confidence_score']}",
        confidence=spec["confidence_score"]
    )

    return spec