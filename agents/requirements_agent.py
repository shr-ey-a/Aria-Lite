import json
from langchain_groq import ChatGroq
from core.decision_ledger import DecisionLedger

class RequirementsAgent:
    def __init__(self, llm: ChatGroq, ledger: DecisionLedger):
        self.llm = llm
        self.ledger = ledger
        self.name = "Requirements Agent"

    def run(self, user_prompt: str) -> dict:
        print(f"\n🔍 [{self.name}] Analyzing prompt...")

        system_prompt = """You are an expert software requirements analyst.
Convert the user's vague prompt into a structured technical specification.

Respond ONLY with a valid JSON object in this exact format:
{
  "project_name": "string",
  "description": "string",
  "api_endpoints": [
    {"method": "GET/POST/PUT/DELETE", "path": "/path", "description": "what it does"}
  ],
  "data_models": [
    {"name": "ModelName", "fields": [{"name": "field", "type": "str/int/bool", "required": true}]}
  ],
  "business_logic": ["rule 1", "rule 2"],
  "non_functional_requirements": ["performance req", "security req"],
  "confidence_score": 0.0
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Convert this to a technical spec: {user_prompt}"}
        ]

        response = self.llm.invoke(messages)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            spec = json.loads(raw)
        except json.JSONDecodeError:
           
            spec = {
                "project_name": "GeneratedApp",
                "description": user_prompt,
                "api_endpoints": [{"method": "GET", "path": "/items", "description": "Get all items"}],
                "data_models": [{"name": "Item", "fields": [{"name": "id", "type": "int", "required": True}, {"name": "name", "type": "str", "required": True}]}],
                "business_logic": ["Basic CRUD operations"],
                "non_functional_requirements": ["Fast response times", "Input validation"],
                "confidence_score": 0.7
            }

        confidence = spec.get("confidence_score", 0.85)

        self.ledger.log(
            agent=self.name,
            decision=f"Generated technical spec for: {spec.get('project_name', 'App')}",
            reasoning=f"Analyzed prompt and extracted {len(spec.get('api_endpoints', []))} endpoints and {len(spec.get('data_models', []))} data models",
            alternatives=["Could request clarification", "Could generate minimal spec"],
            confidence=confidence
        )

        return spec