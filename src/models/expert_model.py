import os
import logging
from abc import ABC, abstractmethod
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpertModel(ABC):
    @abstractmethod
    async def predict(self, query, context):
        pass

class AzureMLExpertModel(ExpertModel):
    def __init__(self, endpoint_url, api_key):
        self.endpoint_url = endpoint_url
        self.api_key = api_key

    async def predict(self, query, context):
        """Call an Azure ML Online Endpoint."""
        if not self.endpoint_url:
            return f"Simulated Insight: Focus on {query[:10]} in context of {context[:10]}."

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "input_data": {
                "columns": ["query", "context"],
                "data": [[query, context]]
            }
        }
        
        try:
            # In a real async scenario, use httpx or aiohttp
            response = requests.post(self.endpoint_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()[0]
        except Exception as e:
            logger.error(f"Error calling Azure ML endpoint: {e}")
            return f"Error: Could not reach expert model. {str(e)}"

class BaselinePolicyModel(ExpertModel):
    async def predict(self, query, context):
        """A simple baseline model that uses heuristics."""
        logger.info("Using Baseline Policy Model")
        if "infrastructure" in query.lower():
            return "Infrastructure Recommendation: Ensure all schools have broadband connectivity."
        elif "policy" in query.lower():
            return "Policy Recommendation: Align with the latest 2024 Educational Standards."
        else:
            return "General Recommendation: Refer to the DBE Master Plan."
