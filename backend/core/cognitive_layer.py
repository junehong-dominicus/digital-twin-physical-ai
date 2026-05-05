import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

class CognitiveLayer:
    """
    The 'Cognitive Layer' of the Digital Twin.
    Uses LLMs to reason about system state and Edge AI anomalies.
    """
    def __init__(self, model_name="gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("your_"):
            self.llm = ChatOpenAI(model=model_name, temperature=0.2)
            self.is_mock = False
        else:
            # Fallback to a mock for demo purposes if no API key is provided
            self.is_mock = True
            print("⚠️ [COGNITIVE_LAYER] OPENAI_API_KEY not found. Using Mock Reasoning Engine.")

        # System prompt defining the "Reasoning Agent" persona
        self.system_template = """
        You are the Cognitive Layer of an Industrial Digital Twin.
        Your goal is to analyze real-time telemetry and Edge AI insights to provide
        root-cause analysis and actionable troubleshooting advice.
        
        System State:
        {state_json}
        
        Industrial Guidelines:
        - If vibration anomaly score > 0.7, check bearing lubrication immediately.
        - If temperature > 80C and anomaly score > 0.5, initiate emergency shutdown.
        - Always reference specific Edge AI scores in your response.
        """
        self.prompt = ChatPromptTemplate.from_template(self.system_template)

    def analyze_system_state(self, state_summary: Dict[str, Any]) -> str:
        """
        Asks the LLM to provide a reasoning-based summary and action plan.
        """
        import json
        state_str = json.dumps(state_summary, indent=2)
        
        if self.is_mock:
            # Simple heuristic mock reasoning for the demo
            if state_summary.get("health_score", 1.0) < 0.5:
                return (
                    "### 🚨 COGNITIVE ANALYSIS (MOCK)\n"
                    "**Root Cause**: Critical Anomaly detected in Vibration sensors.\n"
                    "**Edge AI Insight**: Anomaly Score is high (0.88). Alert: 'Critical Bearing Resonance'.\n"
                    "**Recommendation**: Immediately investigate bearing lubrication and alignment. "
                    "The current vibration pattern suggests imminent failure of the primary shaft."
                )
            return "### ✅ COGNITIVE ANALYSIS (MOCK)\nSystem is operating within nominal parameters. No action required."

        chain = self.prompt | self.llm
        response = chain.invoke({"state_json": state_str})
        return response.content

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
