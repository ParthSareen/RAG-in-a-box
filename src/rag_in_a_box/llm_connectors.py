import openai
import ollama

messages = [
    {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the user's question."},
]

def format_chat_history(chat_history):
    formatted_history = []
    for human, assistant in chat_history:
        formatted_history.append({"role": "user", "content": human})
        formatted_history.append({"role": "assistant", "content": assistant})
    return formatted_history

def get_llm_response_openai(query: str, context: str, model: str, chat_history=None):
    current_messages = messages.copy()
    if chat_history:
        current_messages.extend(format_chat_history(chat_history))

    current_messages.append({"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"})
    
    response = openai.chat.completions.create(
        model=model,
        messages=current_messages,
        stream=True
    )
    return response


def get_llm_response_ollama(query: str, context: str, model: str, chat_history=None):
    current_messages = messages.copy()
    if chat_history:
        current_messages.extend(format_chat_history(chat_history))

    current_messages.append({"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"})
    response = ollama.chat(
        model=model,
        messages=current_messages,
        stream=True
    )
    return response
