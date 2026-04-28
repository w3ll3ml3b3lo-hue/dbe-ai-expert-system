import os
from gremlin_python.driver import client, serializer

class KnowledgeGraphManager:
    def __init__(self, endpoint, key, database_name, graph_name):
        # Format the endpoint for Gremlin
        self.endpoint = endpoint.replace("https://", "wss://").replace(".documents.azure.com:443/", ".gremlin.cosmos.azure.com:443/")
        self.key = key
        self.client = client.Client(
            self.endpoint, 'g',
            username=f"/dbs/{database_name}/colls/{graph_name}",
            password=self.key,
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

    def initialize_graph(self):
        """Initialize the graph with core vertex types for the DBE Expert System."""
        print("Initializing Knowledge Graph structure...")
        
        # Add core nodes if they don't exist
        queries = [
            "g.addV('ExpertSystem').property('id', 'dbe_root').property('name', 'DBE AI Expert System')",
            "g.addV('Category').property('id', 'policy').property('name', 'Educational Policy')",
            "g.addV('Category').property('id', 'infrastructure').property('name', 'School Infrastructure')",
            "g.V('dbe_root').addE('manages').to(g.V('policy'))",
            "g.V('dbe_root').addE('manages').to(g.V('infrastructure'))"
        ]
        
        for q in queries:
            try:
                self.client.submit(q).all().result()
                print(f"Executed: {q}")
            except Exception as e:
                print(f"Error executing {q}: {e}")

    def add_document_node(self, doc_id, doc_name, category_id):
        """Link a document to a category in the graph."""
        if not self.validate_schema("Document"):
            raise ValueError("Schema validation failed for vertex label 'Document'")
            
        query = f"g.addV('Document').property('id', '{doc_id}').property('name', '{doc_name}')"
        self.client.submit(query).all().result()
        
        link_query = f"g.V('{category_id}').addE('contains').to(g.V('{doc_id}'))"
        self.client.submit(link_query).all().result()
        print(f"Added document {doc_name} to category {category_id}")

    def validate_schema(self, label):
        """Verify if a label is part of the allowed schema."""
        allowed_labels = ["ExpertSystem", "Category", "Document", "Agent"]
        return label in allowed_labels

    def get_schema_definition(self):
        """Returns the current graph schema definition."""
        return {
            "vertices": ["ExpertSystem", "Category", "Document", "Agent"],
            "edges": ["manages", "contains", "references", "triggers"]
        }

if __name__ == "__main__":
    # Placeholder for credentials
    ENDPOINT = os.getenv("COSMOS_GREMLIN_ENDPOINT")
    KEY = os.getenv("COSMOS_GREMLIN_KEY")
    
    if ENDPOINT and KEY:
        manager = KnowledgeGraphManager(ENDPOINT, KEY, "KnowledgeDB", "ExpertGraph")
        manager.initialize_graph()
    else:
        print("COSMOS_GREMLIN_ENDPOINT or COSMOS_GREMLIN_KEY not set.")
