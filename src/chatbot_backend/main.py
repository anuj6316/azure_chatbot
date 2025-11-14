import gradio as gr
from ..core.config import get_vectorstore
from ..core import retriver, chat_manager


def chat_function(message, history):
    try:
        vectorstore = get_vectorstore()
    except RuntimeError as exc:
        return f"Error: {exc}"

    try:
        relevant_docs = retriver.get_relevant_docs(vectorstore, message)
        llm = chat_manager.get_llm()
        result = chat_manager.generate_response(llm, relevant_docs, message)

        response = result["answer"]
        if result["context_used"]:
            context_text = "\n".join([doc.page_content for doc in relevant_docs])
            response += f"\n\n---\n\n**Context used:**\n{context_text}"
        return response
    except Exception as exc:
        return f"Error generating response: {exc}"


with gr.Blocks() as demo:
    gr.ChatInterface(
        fn=chat_function,
        chatbot=gr.Chatbot(height=600, type="messages"),
        textbox=gr.Textbox(
            placeholder="Ask a question about your documents...", label="Question"
        ),
        title="RAG Chatbot",
        description="Ask questions about your knowledge base.",
        type="messages",
    )

demo.launch()
