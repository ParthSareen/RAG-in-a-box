import gradio as gr
from typing import List, Dict
from main import load_documents
from llm_connectors import get_llm_response_openai, get_llm_response_ollama
from common_utils import store_documents, search_documents, process_search_results
from db_connectors.chroma_connector import ChromaConnector

def load_and_store_documents(loader_type: str, path: str, persist_path: str):
    documents = load_documents(loader_type, path)
    connector = store_documents(documents, persist_path)
    return f"Loaded and stored {len(documents)} documents"

def process_query(query: str, history: str, loader_type: str, path: str, persist_path: str, model: str):
    # Search for relevant documents
    connector = ChromaConnector(persist_path) 
    results = search_documents(connector, query)

    
    # Process results
    context = process_search_results(results)
    
    # Get response from LLM
    if model.startswith('gpt'):
        response = get_llm_response_openai(query, context, model, history)
        answer = ''.join(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
    else:
        response = get_llm_response_ollama(query, context, model, history)
        answer = ''.join(chunk['message']['content'] for chunk in response)
    return answer

def launch_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# RAG in a Box")
        
        with gr.Row():
            loader_type = gr.Radio(["pdf", "md"], label="Loader Type", value="pdf")
            path = gr.Textbox(label="Document Path")
            persist_path = gr.Textbox(label="Persist Path", value="./chroma_db")
            model = gr.Textbox(label="Model Name", value="gpt-4o-mini-2024-07-18")
        
        load_btn = gr.Button("Load and Store Documents")
        load_output = gr.Textbox(label="Load Status")
        
        load_btn.click(
            load_and_store_documents,
            inputs=[loader_type, path, persist_path],
            outputs=load_output
        )
        
        chatbot = gr.ChatInterface(
            process_query,
            additional_inputs=[loader_type, path, persist_path, model],
            description="Ask questions about your documents",
            cache_examples=False,
        )
    
    demo.launch()

if __name__ == "__main__":
    launch_interface()
