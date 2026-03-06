# core/orchestrator.py
import os
from langchain_groq import ChatGroq
from core.decision_ledger import DecisionLedger
from agents.requirements_agent import RequirementsAgent
from agents.architect_agent import ArchitectAgent
from agents.code_agent import CodeAgent
from agents.test_agent import TestAgent

class ARIAOrchestrator:
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            api_key=groq_api_key,
          model_name="llama-3.3-70b-versatile",
            temperature=0.3
        )
        self.ledger = DecisionLedger()

        self.req_agent = RequirementsAgent(self.llm, self.ledger)
        self.arch_agent = ArchitectAgent(self.llm, self.ledger)
        self.code_agent = CodeAgent(self.llm, self.ledger)
        self.test_agent = TestAgent(self.llm, self.ledger)

    def run_pipeline(self, user_prompt: str, progress_callback=None) -> dict:
        results = {}

        def update(msg, pct):
            print(msg)
            if progress_callback:
                progress_callback(msg, pct)

        update("🔍 Agent 1: Analyzing requirements...", 10)
        spec = self.req_agent.run(user_prompt)
        results["spec"] = spec
        update("✅ Requirements spec generated", 25)

        update("🏛️ Agent 2: Designing architecture...", 30)
        architecture = self.arch_agent.run(spec)
        results["architecture"] = architecture
        update("✅ Architecture designed", 50)

        update("💻 Agent 3: Generating code...", 55)
        code = self.code_agent.run(spec, architecture)
        results["code"] = code
        update("✅ Code generated", 75)

        update("🧪 Agent 4: Writing test suite...", 80)
        tests = self.test_agent.run(spec, code["files"])
        results["tests"] = tests
        update("✅ Tests generated", 95)

        results["ledger"] = self.ledger.get_all()
        results["ledger_markdown"] = self.ledger.to_markdown()
        update("🎉 Pipeline complete!", 100)

        return results