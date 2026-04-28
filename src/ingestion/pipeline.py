import os
import json
import logging
from azure.cosmos import CosmosClient, PartitionKey
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeIngestionPipeline:
    def __init__(self, cosmos_endpoint, cosmos_key, database_name, container_name, blob_connection_string=None):
        self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
        self.database = self.cosmos_client.create_database_if_not_exists(id=database_name)
        self.container = self.database.create_container_if_not_exists(
            id=container_name, 
            partition_key=PartitionKey(path="/partitionKey"),
            offer_throughput=400
        )
        
        if blob_connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        else:
            logger.warning("Blob connection string not provided. Blob operations will be disabled.")
            self.blob_service_client = None

    def ingest_from_blob(self, container_name, blob_name):
        """Download a blob and ingest it into Cosmos DB."""
        if not self.blob_service_client:
            logger.error("Blob service client not initialized.")
            return

        logger.info(f"Ingesting from blob: {container_name}/{blob_name}")
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        download_stream = blob_client.download_blob()
        data = json.loads(download_stream.readall())
        
        self.upsert_to_cosmos(data, source=blob_name)

    def ingest_document(self, doc_path):
        """Ingest a single local document into the Knowledge Store."""
        logger.info(f"Ingesting local document: {doc_path}")
        with open(doc_path, 'r') as f:
            data = json.load(f)
        
        self.upsert_to_cosmos(data, source=os.path.basename(doc_path))

    def upsert_to_cosmos(self, data, source):
        """Helper to upsert data to Cosmos DB with metadata."""
        data['id'] = data.get('id', source)
        data['partitionKey'] = data.get('category', 'default')
        data['source'] = source
        
        self.container.upsert_item(data)
        logger.info(f"Successfully upserted {data['id']} to Cosmos DB.")

if __name__ == "__main__":
    COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
    COSMOS_KEY = os.getenv("COSMOS_KEY")
    BLOB_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    if COSMOS_ENDPOINT and COSMOS_KEY:
        pipeline = KnowledgeIngestionPipeline(
            COSMOS_ENDPOINT, 
            COSMOS_KEY, 
            "KnowledgeDB", 
            "IntelligenceStore",
            blob_connection_string=BLOB_CONN_STR
        )
        # Example: pipeline.ingest_document("data/sample.json")
    else:
        logger.warning("COSMOS_ENDPOINT or COSMOS_KEY not set. Skipping ingestion.")
