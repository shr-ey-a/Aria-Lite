import json
from datetime import datetime

class DecisionLedger:
    def __init__(self):
        self.entries = []

    def log(self, agent, decision, reasoning, confidence):
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence
        }
        self.entries.append(entry)
        return entry

    def get_all(self):
        return self.entries