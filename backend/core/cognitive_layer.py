import sys
import os
import json
import requests
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class CognitiveLayer:
    """
    The 'Cognitive Layer' of the Digital Twin.
    Uses LLMs to reason about system state, spatial events, and Edge AI anomalies.
    """
    def __init__(self, model_name="gpt-4o", api_url="http://127.0.0.1:8001"):
        self.api_url = api_url
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key and not api_key.startswith("your_"):
            self.llm = ChatOpenAI(model=model_name, temperature=0.2)
            self.is_mock = False
        else:
            self.is_mock = True
            print("⚠️ [COGNITIVE_LAYER] OPENAI_API_KEY not found. Using Mock Reasoning Engine.")

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Cognitive Layer of an Industrial Digital Twin.
You monitor a system of sensors, CCTV cameras, and autonomous agents (robots/drones).

Your inputs are:
1. A structured JSON summary of the system state.
2. Recent Spatial Event History (from API).
3. A user question or analysis request.

Guidelines:
- Analyze correlations (e.g., vibration anomalies linked to zone occupancy).
- If an agent has low battery or a fault, prioritize it.
- Explain *why* events are happening based on history (e.g., "Robot stopped because person entered zone").
- Reference specific Edge AI scores (0.0 to 1.0) in your reasoning."""),
            ("user", """Current System State:
{state_json}

Recent Event History:
{history_json}

Request/Question: {question}""")
        ])

        if not self.is_mock:
            self.chain = self.prompt | self.llm | StrOutputParser()

    def _fetch_history(self) -> List[Dict]:
        """Helper to fetch event history from the API."""
        try:
            response = requests.get(f"{self.api_url}/events/history", params={"limit": 10}, timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            return []
        return []

    def analyze_system_state(self, state_summary: Dict[str, Any], question: str = "Provide a general health assessment.") -> str:
        """
        Queries the LLM for reasoning-based analysis.
        """
        state_json = json.dumps(state_summary, indent=2)
        history = self._fetch_history()
        history_json = json.dumps(history, indent=2) if history else "No history available."
        
        if self.is_mock:
            if state_summary.get("health_score", 1.0) < 0.6:
                return "### 🚨 COGNITIVE ANALYSIS (MOCK)\nAnomaly detected. Correlation: Zone occupancy high near critical pump."
            return "### ✅ COGNITIVE ANALYSIS (MOCK)\nAll systems nominal."

        return self.chain.invoke({
            "state_json": state_json,
            "history_json": history_json,
            "question": question
        })

# Example usage for demo
if __name__ == "__main__":
    try:
        from backend.core.twin_state import SystemTwin
    except ImportError:
        from twin_state import SystemTwin
    twin = SystemTwin()
    
    # Simulate an anomaly from Edgie AI
    twin.update_environment({
        "temperature": 82.5,
        "vibration": 0.08,
        "edge_ai": {
            "score": 0.85,
            "alert": "Critical Overheating"
        }
    })
    
    cognitive = CognitiveLayer()
    summary = twin.get_state_summary_for_llm()
    print("--- COGNITIVE REASONING ---")
    print(cognitive.analyze_system_state(summary))
