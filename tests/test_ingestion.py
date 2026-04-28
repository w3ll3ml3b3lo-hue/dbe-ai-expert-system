import unittest
from unittest.mock import MagicMock, patch
from src.ingestion.pipeline import KnowledgeIngestionPipeline

class TestKnowledgeIngestionPipeline(unittest.TestCase):
    @patch('src.ingestion.pipeline.CosmosClient')
    def setUp(self, mock_cosmos):
        self.mock_cosmos = mock_cosmos
        self.mock_db = MagicMock()
        self.mock_container = MagicMock()
        self.mock_cosmos.return_value.create_database_if_not_exists.return_value = self.mock_db
        self.mock_db.create_container_if_not_exists.return_value = self.mock_container
        
        self.pipeline = KnowledgeIngestionPipeline(
            "https://fake.cosmos.azure.com:443/", 
            "fakekey", 
            "testdb", 
            "testcontainer"
        )

    def test_upsert_to_cosmos(self):
        data = {"content": "test content", "category": "policy"}
        self.pipeline.upsert_to_cosmos(data, source="test.json")
        
        self.mock_container.upsert_item.assert_called_once()
        args, _ = self.mock_container.upsert_item.call_args
        upserted_data = args[0]
        
        self.assertEqual(upserted_data['id'], "test.json")
        self.assertEqual(upserted_data['partitionKey'], "policy")
        self.assertEqual(upserted_data['source'], "test.json")

if __name__ == '__main__':
    unittest.main()
