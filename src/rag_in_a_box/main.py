import argparse
from pathlib import Path
from typing import List, Dict

from llm_connectors import get_llm_response_openai, get_llm_response_ollama
from common_utils import store_documents, search_documents, process_search_results, load_documents
from db_connectors.chroma_connector import ChromaConnector


def main():
    parser = argparse.ArgumentParser(description="Document loader and Q&A system")
    parser.add_argument("--loader_type", choices=['pdf', 'md'], default='pdf', help="Type of document loader")
    parser.add_argument("--path", help="Path to the directory containing documents")
    parser.add_argument("--persist_path", default="./chroma_db", help="Path to persist the vector database")
    parser.add_argument("--model", default="gpt-4o-mini-2024-07-18", help="OpenAI or Ollama model to use for Q&A")
    args = parser.parse_args()

    if args.path:
        # Load documents
        documents = load_documents(args.loader_type, args.path)
        print(f"Loaded {len(documents)} documents")

        # Store documents in vector database
        connector = store_documents(documents, args.persist_path)
        print("Documents stored in vector database")
    else:
        # Initialize connector without loading documents
        connector = ChromaConnector(args.persist_path)

    # Q&A loop
    while True:
        query = input("Enter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break

        # Search for relevant documents
        results = search_documents(connector, query)

        # Process results
        context = process_search_results(results)

        # Get response from LLM
        if args.model.startswith('gpt'):
            response = get_llm_response_openai(query, context, args.model)
            print("Answer:", end=" ", flush=True)
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="", flush=True)
        else:
            response = get_llm_response_ollama(query, context, args.model)
            print("Answer:", end=" ", flush=True)
            for chunk in response:
                print(chunk['message']['content'], end='', flush=True)
        print()

if __name__ == "__main__":
    main()