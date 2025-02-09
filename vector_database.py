import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
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
# print("PDF pages: ", len(documents))

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

# model_name="sentence-transformers/all-MiniLM-L6-v2"
# def get_embedding_model(model_name=model_name):
#     embeddings = HuggingFaceEmbeddings(model_name=model_name)
#     return embeddings

# # Step 4: Index Documents **Store embeddings in FAISS (vector store)
# FAISS_DB_PATH = "vectorstore/db_faiss"
# faiss_db = FAISS.from_documents(text_chunks, get_embedding_model(model_name))
# faiss_db.save_local(FAISS_DB_PATH)

from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from bson import ObjectId

MONGO_URI = "mongodb+srv://manali0210:TrBaO7bfGRxSFzyy@cluster0.pjfepaj.mongodb.net/"
DATABASE_NAME = "vector_db"
COLLECTION_NAME = "embeddings"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

from langchain.embeddings import HuggingFaceEmbeddings

# Load the embedding model
def get_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return HuggingFaceEmbeddings(model_name=model_name)

embeddings = get_embedding_model()

def store_in_mongo(text_chunks):
    documents = []
    existing_ids = {doc["_id"] for doc in collection.find({}, {"_id": 1})}  # Get existing IDs

    for i, chunk in enumerate(text_chunks):
        embedding = embeddings.embed_query(chunk.page_content)  # Generate vector
        new_id = ObjectId()  # Generate a unique ObjectId

        # Ensure the generated _id is not a duplicate (if using sequential numbers)
        while new_id in existing_ids:
            new_id = ObjectId()

        document = {
            "_id": new_id,  # Unique ID
            "text": chunk.page_content,
            "embedding": embedding
        }
        documents.append(document)

    try:
        collection.insert_many(documents, ordered=False)  # Insert all at once, continue on error
        print("✅ Embeddings stored in MongoDB successfully.")
    except BulkWriteError as e:
        print("⚠️ Bulk write error:", e.details)  # Print error details
        
# Store chunks in MongoDB
store_in_mongo(text_chunks)