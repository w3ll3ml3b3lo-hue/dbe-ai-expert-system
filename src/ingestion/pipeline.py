import os
import json
from azure.cosmos import CosmosClient, PartitionKey
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeIngestionPipeline:
    def __init__(self, endpoint, key, database_name, container_name):
        self.client = CosmosClient(endpoint, key)
        self.database = self.client.create_database_if_not_exists(id=database_name)
        self.container = self.database.create_container_if_not_exists(
            id=container_name, 
            partition_key=PartitionKey(path="/partitionKey"),
            offer_throughput=400
        )

    def ingest_document(self, doc_path):
        """Ingest a single document into the Knowledge Graph/Store."""
        logger.info(f"Ingesting document: {doc_path}")
        with open(doc_path, 'r') as f:
            data = json.load(f)
        
        # Add metadata or transform data if necessary
        data['id'] = data.get('id', os.path.basename(doc_path))
        data['partitionKey'] = data.get('category', 'default')
        
        self.container.upsert_item(data)
        logger.info(f"Successfully ingested {data['id']}")

if __name__ == "__main__":
    # Placeholder for environment variables
    COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
    COSMOS_KEY = os.getenv("COSMOS_KEY")
    
    if COSMOS_ENDPOINT and COSMOS_KEY:
        pipeline = KnowledgeIngestionPipeline(
            COSMOS_ENDPOINT, 
            COSMOS_KEY, 
            "KnowledgeDB", 
            "IntelligenceStore"
        )
        # Example: pipeline.ingest_document("data/sample.json")
    else:
        logger.warning("COSMOS_ENDPOINT or COSMOS_KEY not set. Skipping ingestion.")
