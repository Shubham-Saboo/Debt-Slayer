import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()
# Step 1: Load raw PDFs from the directory
pdfs_directory = 'pdfs/'

def load_pdfs_from_directory(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            loader = PDFPlumberLoader(file_path)
            documents.extend(loader.load())
    return documents

documents = load_pdfs_from_directory(pdfs_directory)
print("PDF pages: ", len(documents))

# Step 2: Create Chunks
def create_chunks(documents): 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    text_chunks = text_splitter.split_documents(documents)
    return text_chunks

text_chunks = create_chunks(documents)
print("Chunks count: ", len(text_chunks))

# Step 3: Setup Embeddings Model (Use DeepSeek R1 with Ollama)
# model_name = "deepseek-r1:14b"
# def get_embedding_model(ollama_model_name):
#     embeddings = OllamaEmbeddings(model=ollama_model_name)
#     return embeddings

from langchain.embeddings import HuggingFaceEmbeddings
model_name="sentence-transformers/all-MiniLM-L6-v2"
def get_embedding_model(model_name=model_name):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings

# Step 4: Index Documents **Store embeddings in FAISS (vector store)
FAISS_DB_PATH = "vectorstore/db_faiss"
faiss_db = FAISS.from_documents(text_chunks, get_embedding_model(model_name))
faiss_db.save_local(FAISS_DB_PATH)