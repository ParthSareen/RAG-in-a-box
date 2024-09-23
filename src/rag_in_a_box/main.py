import argparse
from pathlib import Path
from typing import List, Dict

from loaders.pdf_loader import PdfLoader
from loaders.markdown_loader import MarkdownLoader
from db_connectors.chroma_connector import ChromaConnector
from db_connectors.marqo_connector import MarqoConnector

import openai

def load_documents(loader_type: str, directory_path: str) -> List[Dict[str, str]]:
    if loader_type == 'pdf':
        loader = PdfLoader(directory_path)
    elif loader_type == 'md':
        loader = MarkdownLoader(directory_path)
    else:
        raise ValueError(f"Unsupported loader type: {loader_type}")
    return loader.load()

def store_documents(connector_type: str, documents: List[Dict[str, str]], persist_path: str = None):
    if connector_type == 'chroma':
        connector = ChromaConnector(persist_path or "./chroma_db")
        connector.add_documents("default_collection", documents)
    elif connector_type == 'marqo':
        connector = MarqoConnector()
        connector.create_index("default_index", model="hf/e5-base-v2")
        connector.add_documents("default_index", documents, tensor_fields=["content"])
    else:
        raise ValueError(f"Unsupported connector type: {connector_type}")
    return connector

def search_documents(connector, query: str, connector_type: str):
    if connector_type == 'chroma':
        return connector.search("default_collection", query)
    elif connector_type == 'marqo':
        return connector.search("default_index", query)

def get_llm_response(query: str, context: str, model: str):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the user's question."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    return response

def main():
    parser = argparse.ArgumentParser(description="Document loader and Q&A system")
    parser.add_argument("--loader", choices=['pdf', 'md'], default='pdf', help="Type of document loader")
    parser.add_argument("--connector", choices=['chroma', 'marqo'], default='chroma', help="Type of vector database connector")
    parser.add_argument("--path", help="Path to the directory containing documents")
    parser.add_argument("--persist_path", help="Path to persist the vector database (for Chroma)")
    parser.add_argument("--load", action="store_true", help="Load and store documents before starting Q&A")
    parser.add_argument("--model", default="gpt-4o-mini-2024-07-18", help="OpenAI or Ollama model to use for Q&A")
    args = parser.parse_args()

    if args.load:
        if not args.path:
            print("Error: --path is required when --load is specified")
            return

        # Load documents
        documents = load_documents(args.loader, args.path)
        print(f"Loaded {len(documents)} documents")

        # Store documents in vector database
        connector = store_documents(args.connector, documents, args.persist_path)
        print("Documents stored in vector database")
    else:
        # Initialize connector without loading documents
        if args.connector == 'chroma':
            connector = ChromaConnector(args.persist_path or "./chroma_db")
        elif args.connector == 'marqo':
            connector = MarqoConnector()
        else:
            raise ValueError(f"Unsupported connector type: {args.connector}")

    # Q&A loop
    while True:
        query = input("Enter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break

        # Search for relevant documents
        results = search_documents(connector, query, args.connector)

        # Process results based on connector type
        if args.connector == 'chroma':
            context = "\n".join(results['documents'][0])
        elif args.connector == 'marqo':
            context = "\n".join([hit['content'] for hit in results['hits']])

        # Get response from LLM
        response = get_llm_response(query, context, args.model)
        print("Answer:", end=" ", flush=True)
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()

if __name__ == "__main__":
    main()