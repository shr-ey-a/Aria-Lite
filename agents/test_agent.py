import json
import os
from langchain_groq import ChatGroq
from core.decision_ledger import DecisionLedger

class TestAgent:
    def __init__(self, llm: ChatGroq, ledger: DecisionLedger):
        self.llm = llm
        self.ledger = ledger
        self.name = "Test Agent"

    def run(self, spec: dict, code_files: dict) -> dict:
        print(f"\n🧪 [{self.name}] Generating test suite...")

        system_prompt = """You are a senior QA engineer.
Generate a comprehensive pytest test suite from the requirements spec.
Tests should validate business logic, not just implementation.

Respond with ONLY the raw Python test code. No markdown, no explanation.
Include: unit tests, integration tests, edge cases.
Use TestClient from FastAPI for API testing.
Import from: from main import app, from database import engine, Base"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate pytest tests for:\n{json.dumps(spec, indent=2)}"}
        ]

        response = self.llm.invoke(messages)
        test_code = response.content.strip()

        if test_code.startswith("```"):
            test_code = test_code.split("```")[1]
            if test_code.startswith("python"):
                test_code = test_code[6:]
        test_code = test_code.strip()

        # Ensure it has fallback
        if "def test_" not in test_code:
            test_code = self._fallback_tests(spec)

        os.makedirs("outputs/generated_app", exist_ok=True)
        test_path = "outputs/generated_app/test_app.py"
        with open(test_path, "w") as f:
            f.write(test_code)

        test_count = test_code.count("def test_")

        self.ledger.log(
            agent=self.name,
            decision=f"Generated {test_count} test functions from requirements spec",
            reasoning="Tests derived from spec (not code) to validate business logic independently",
            alternatives=["Test from code implementation", "Manual test writing"],
            confidence=0.87
        )

        return {"test_code": test_code, "test_count": test_count, "path": test_path}

    def _fallback_tests(self, spec: dict) -> str:
        return '''import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from database import engine, Base

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_create_item():
    response = client.post("/api/v1/items", json={"title": "Test Item", "description": "A test"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["completed"] == False

def test_get_items_empty():
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_items_after_create():
    client.post("/api/v1/items", json={"title": "Item 1"})
    client.post("/api/v1/items", json={"title": "Item 2"})
    response = client.get("/api/v1/items")
    assert len(response.json()) >= 2

def test_get_single_item():
    create = client.post("/api/v1/items", json={"title": "Single"})
    item_id = create.json()["id"]
    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id

def test_item_not_found():
    response = client.get("/api/v1/items/99999")
    assert response.status_code == 404

def test_update_item():
    create = client.post("/api/v1/items", json={"title": "Old Title"})
    item_id = create.json()["id"]
    response = client.put(f"/api/v1/items/{item_id}", json={"title": "New Title", "completed": True})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["completed"] == True

def test_delete_item():
    create = client.post("/api/v1/items", json={"title": "To Delete"})
    item_id = create.json()["id"]
    delete = client.delete(f"/api/v1/items/{item_id}")
    assert delete.status_code == 200
    get = client.get(f"/api/v1/items/{item_id}")
    assert get.status_code == 404

def test_create_item_missing_title():
    response = client.post("/api/v1/items", json={"description": "No title"})
    assert response.status_code == 422  # Validation error
'''