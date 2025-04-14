# 📄 classify_task.py
# 📍 Location: backend/app/core/classify_task.py
# 🧠 Purpose: Contains logic to classify a user task based on intent, LLM requirement, and cost

from typing import Dict

# Example simple classification function
# In production this could leverage OpenAI or keyword-based heuristics

def classify_task(user_input: str) -> Dict:
    """
    Classify the task based on intent, LLM capability required, and estimated cost.
    """
    task = user_input.lower()

    if "summarize" in task:
        return {
            "intent": "summarization",
            "llm": "gpt-4",
            "cost": "high",
            "agent": "Planner"
        }
    elif "retrieve" in task or "find" in task:
        return {
            "intent": "retrieval",
            "llm": "gpt-3.5",
            "cost": "low",
            "agent": "ContactCenterAgent"
        }
    elif "compliance" in task:
        return {
            "intent": "compliance_query",
            "llm": "gpt-4",
            "cost": "medium",
            "agent": "ComplianceAgent"
        }
    else:
        return {
            "intent": "general_query",
            "llm": "gpt-3.5",
            "cost": "medium",
            "agent": "Planner"
        }