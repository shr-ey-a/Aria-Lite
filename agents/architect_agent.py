import json
from langchain_groq import ChatGroq
from core.decision_ledger import DecisionLedger

class ArchitectAgent:
    def __init__(self, llm: ChatGroq, ledger: DecisionLedger):
        self.llm = llm
        self.ledger = ledger
        self.name = "Architect Agent"

    def run(self, spec: dict) -> dict:
        print(f"\n🏛️ [{self.name}] Designing architecture...")

        system_prompt = """You are a senior software architect.
Given a technical specification, design the system architecture.

Respond ONLY with a valid JSON object in this exact format:
{
  "database": "SQLite or PostgreSQL",
  "database_reason": "why this was chosen",
  "api_style": "REST or GraphQL",
  "api_reason": "why this was chosen",
  "architecture_pattern": "monolith or microservices",
  "pattern_reason": "why",
  "tech_stack": {
    "backend": "FastAPI",
    "orm": "SQLAlchemy",
    "validation": "Pydantic",
    "testing": "pytest"
  },
  "deployment_strategy": "string",
  "folder_structure": ["list", "of", "folders"],
  "design_decisions": ["decision 1", "decision 2"]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Design architecture for this spec:\n{json.dumps(spec, indent=2)}"}
        ]

        response = self.llm.invoke(messages)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            architecture = json.loads(raw)
        except json.JSONDecodeError:
            architecture = {
                "database": "SQLite",
                "database_reason": "Lightweight, zero-config, perfect for prototype",
                "api_style": "REST",
                "api_reason": "Industry standard, well-understood",
                "architecture_pattern": "monolith",
                "pattern_reason": "Simpler for initial build",
                "tech_stack": {"backend": "FastAPI", "orm": "SQLAlchemy", "validation": "Pydantic", "testing": "pytest"},
                "deployment_strategy": "Uvicorn ASGI server with hot reload",
                "folder_structure": ["app/", "app/models/", "app/routes/", "tests/"],
                "design_decisions": ["REST over GraphQL for simplicity", "SQLite for zero-config setup"]
            }

        self.ledger.log(
            agent=self.name,
            decision=f"Architecture: {architecture.get('architecture_pattern')} with {architecture.get('database')} and {architecture.get('api_style')}",
            reasoning=architecture.get("database_reason", "Best fit for requirements"),
            alternatives=["PostgreSQL for scale", "GraphQL for flexibility", "Microservices for team isolation"],
            confidence=0.88
        )

        return architecture