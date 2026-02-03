import json
import requests
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class DigitalTwinAgent:
    """
    LangChain agent for reasoning about the Digital Twin.
    """
    def __init__(self, model: str = "gpt-4o", api_url: str = "http://127.0.0.1:8001"):
        self.llm = ChatOpenAI(model=model, temperature=0.2)
        self.api_url = api_url
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the AI Cognitive Layer for a Physical Digital Twin.
You monitor a system of sensors, CCTV cameras, mobile robots, and drones.

Your inputs are:
1. A structured JSON summary of the system state (System Twin).
2. Recent Spatial Event History (from API).
3. A user question.

Guidelines:
- Analyze the JSON state deeply. Look for correlations (e.g., vibration + zone occupancy).
- Identify agents by ID and Type.
- If an agent is in a 'fault' state or has low battery, highlight it.
- Explain *why* something might be happening based on the spatial events (e.g., "Robot stopped because an object was detected in its path").
- Use the Event History to answer questions about past detections or changes.
- Do not hallucinate features not present in the JSON."""),
            ("user", """Current System State:
{state_json}

Recent Event History:
{history_json}

Question: {question}""")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def _fetch_history(self) -> list:
        """Helper to fetch event history from the API."""
        try:
            # Timeout is short to prevent blocking if API is down
            response = requests.get(f"{self.api_url}/events/history", params={"limit": 10}, timeout=2)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            # Fail silently/gracefully if API is unreachable
            return []
        return []

    def ask(self, question: str, system_twin: Any) -> str:
        """
        Queries the LLM with the current state of the provided SystemTwin.
        """
        # Extract the state summary using the specific method
        state_summary = system_twin.get_state_summary_for_llm()
        
        # Fetch history from API
        history = self._fetch_history()
        
        # Serialize to JSON for the prompt
        state_json = json.dumps(state_summary, indent=2)
        history_json = json.dumps(history, indent=2) if history else "No history available."
        
        return self.chain.invoke({
            "state_json": state_json,
            "history_json": history_json,
            "question": question
        })