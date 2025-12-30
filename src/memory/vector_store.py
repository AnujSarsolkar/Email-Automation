import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict

class ContextRetriever:
    def __init__(self, persist_path="db_storage"):
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=persist_path)
        
        # Use default embedding function (MiniLM)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="lic_policies",
            embedding_function=self.embedding_fn
        )

    def add_policy_document(self, doc_id: str, text: str, metadata: Dict = None):
        """
        Adds a policy document snippet to the vector database.
        """
        if metadata is None:
            metadata = {}
            
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"Added document {doc_id} to Memory.")

    def retrieve_context(self, query: str, n_results=3) -> List[str]:
        """
        Retrieves relevant policy snippets based on the query.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Flatten results list
        documents = results['documents'][0] if results['documents'] else []
        return documents

    def reset_memory(self):
        """
        Clears the vector database (for testing/reset).
        """
        self.client.delete_collection("lic_policies")
        self.collection = self.client.create_collection("lic_policies")

if __name__ == "__main__":
    # Test
    memory = ContextRetriever()
    
    # Add dummy knowledge
    memory.add_policy_document(
        doc_id="pol_001", 
        text="Claims for maturity must be submitted 30 days prior to the maturity date.",
        metadata={"category": "Claims"}
    )
    memory.add_policy_document(
        doc_id="pol_002", 
        text="Grace period for premium payment is 15 days for monthly mode and 30 days for others.",
        metadata={"category": "Renewal"}
    )
    
    # Query
    query = "How many days grace period for monthly premium?"
    print(f"Query: {query}")
    print(f"Context: {memory.retrieve_context(query)}")
