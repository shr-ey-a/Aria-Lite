# core/decision_ledger.py
import json
import os
from datetime import datetime
from typing import Any

LEDGER_FILE = "outputs/decision_ledger.json"

class DecisionLedger:
    def __init__(self):
        os.makedirs("outputs", exist_ok=True)
        self.entries = []

    def log(self, agent: str, decision: str, reasoning: str, alternatives: list[str] = [], confidence: float = 0.9):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "decision": decision,
            "reasoning": reasoning,
            "alternatives_considered": alternatives,
            "confidence_score": confidence
        }
        self.entries.append(entry)
        self._save()
        return entry

    def _save(self):
        with open(LEDGER_FILE, "w") as f:
            json.dump(self.entries, f, indent=2)

    def get_all(self):
        return self.entries

    def to_markdown(self):
        md = "# 📋 Decision Ledger\n\n"
        for e in self.entries:
            md += f"### [{e['agent']}] — {e['timestamp']}\n"
            md += f"**Decision:** {e['decision']}\n\n"
            md += f"**Reasoning:** {e['reasoning']}\n\n"
            if e['alternatives_considered']:
                md += f"**Alternatives:** {', '.join(e['alternatives_considered'])}\n\n"
            md += f"**Confidence:** {e['confidence_score']}\n\n---\n\n"
        return md