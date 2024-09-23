import chromadb
from typing import List, Dict
from pathlib import Path
from chromadb.utils import embedding_functions
import uuid

class ChromaConnector:
    def __init__(self, persist_path: str):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    def load_documents(self, collection_name: str, documents: List[Dict[str, str]]) -> None:
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

            ids = []
            contents = []
            metadatas = []

            for doc in documents:
                ids.append(str(uuid.uuid4()))
                contents.append(doc['content'])
                metadatas.append({"source": doc['doc_name']})

            collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load documents: {str(e)}")

    def search(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
        try:
            collection = self.client.get_collection(collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to search documents: {str(e)}")


if __name__ == "__main__":
    # Test the ChromaConnector
    persist_path = "./chroma_db"
    connector = ChromaConnector(persist_path)
    collection_name = "test_collection"

    action = input("Do you want to load documents and query (L) or just query (Q)? ").strip().upper()

    if action == 'L':
        # Test loading documents
        test_documents = [
            {"doc_name": "test1.txt", "content": "This is a test document about artificial intelligence."},
            {"doc_name": "test2.txt", "content": "Machine learning is a subset of AI focusing on data and algorithms."},
            {"doc_name": "test3.txt", "content": "Natural language processing is used in many AI applications."}
        ]
        
        print("Loading documents...")
        connector.load_documents(collection_name, test_documents)
        print("Documents loaded successfully.")

    # Test searching
    query = input("Enter your search query: ")
    print(f"\nSearching for: '{query}'")
    results = connector.search(collection_name, query)
    
    print("\nSearch results:")
    for i, (document, metadata, score) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1):
        print(f"{i}. Document: {metadata['source']}")
        print(f"   Content: {document}")
        print(f"   Score: {score}\n")
