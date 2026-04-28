import unittest
import asyncio
from src.models.expert_model import BaselinePolicyModel

class TestExpertModel(unittest.TestCase):
    def setUp(self):
        self.model = BaselinePolicyModel()

    def test_baseline_policy_model_infrastructure(self):
        query = "What is the policy on school infrastructure?"
        context = "Some context"
        
        # Run async method in sync test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.model.predict(query, context))
        
        self.assertIn("Infrastructure Recommendation", result)
        self.assertIn("broadband connectivity", result)

    def test_baseline_policy_model_policy(self):
        query = "Tell me about the educational policy."
        context = "Some context"
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.model.predict(query, context))
        
        self.assertIn("Policy Recommendation", result)
        self.assertIn("2024 Educational Standards", result)

if __name__ == '__main__':
    unittest.main()
