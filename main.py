import streamlit as st
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from rag_pipeline import answer_query, retrieve_docs, get_context
from vector_database import faiss_db




pdfs_directory = 'pdfs/'
llm_model=ChatGroq(model="deepseek-r1-distill-llama-70b")

def answer_query(documents, model, query):
    custom_prompt_template = """
    You are a banker from the fantasy world of Harry Potter. Use the pieces of information provided in the context to answer user's question.
    If you dont know the answer, just say that you dont know, dont try to make up an answer. 
    Dont provide anything out of the given context
    Question: {question} 
    Context: {context} 
    Answer:
    """
    context = get_context(documents)
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | model
    return chain.invoke({"question": query, "context": context})

user_query = st.text_area("Enter your prompt: ", height=150 , placeholder= "Ask Anything!")

ask_question = st.button("Ask AI Lawyer")

if ask_question:

    if user_query:
        retrieved_docs=retrieve_docs(faiss_db, user_query)
        response=answer_query(documents=retrieved_docs, model=llm_model, query=user_query)

        st.chat_message("user").write(user_query)
        st.chat_message("AI Lawyer").write(response)
