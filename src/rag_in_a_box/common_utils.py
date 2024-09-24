from typing import List, Dict
from db_connectors.chroma_connector import ChromaConnector
from rag_in_a_box.loaders.markdown_loader import MarkdownLoader
from rag_in_a_box.loaders.pdf_loader import PdfLoader

def store_documents(documents: List[Dict[str, str]], persist_path: str = None):
    connector = ChromaConnector(persist_path)
    connector.add_documents("default_collection", documents)
    return connector

def search_documents(connector, query: str):
    return connector.search("default_collection", query)

def process_search_results(results: dict) -> str:
    return "\n".join(results['documents'][0])

def load_documents(loader_type: str, directory_path: str) -> List[Dict[str, str]]:
    if loader_type == 'pdf':
        loader = PdfLoader(directory_path)
    elif loader_type == 'md':
        loader = MarkdownLoader(directory_path)
    else:
        raise ValueError(f"Unsupported loader type: {loader_type}")
    return loader.load()