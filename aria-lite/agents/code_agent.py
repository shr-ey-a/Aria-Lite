from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_code_agent(spec, ledger):
    system_prompt = """You are a Code Agent. Generate production-grade FastAPI Python code from a JSON spec.
Include: proper routing, Pydantic models, SQLite via SQLAlchemy, error handling, and comments.
Return ONLY the Python code, no explanations."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate FastAPI code for this spec:\n{str(spec)}"}
        ]
    )

    code = response.choices[0].message.content.strip().strip("```python").strip("```").strip()

    ledger.log(
        agent="Code Agent",
        decision="Generated FastAPI application code",
        reasoning=f"Implemented {len(spec['api_endpoints'])} endpoints with SQLAlchemy ORM and Pydantic validation",
        confidence=0.88
    )

    return code