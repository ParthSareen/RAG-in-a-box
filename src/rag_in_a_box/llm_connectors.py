import openai
import ollama

messages = [
    {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the user's question."},
    ]

def get_llm_response_openai(query: str, context: str, model: str):
    messages.append({"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"})
    
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    return response


def get_llm_response_ollama(query: str, context: str, model: str):
    messages.append({"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"})
    response = ollama.chat(
        model=model,
        messages=messages,
        stream=True
    )
    return response
