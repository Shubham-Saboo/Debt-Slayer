from langchain_groq import ChatGroq
# from vector_database import faiss_db
from langchain_core.prompts import ChatPromptTemplate
import numpy as np
from vector_database import collection, embeddings
# Uncomment the following if you're NOT using pipenv
from dotenv import load_dotenv
load_dotenv()

#Step1: Setup LLM (Use DeepSeek R1 with Groq)
llm_model=ChatGroq(model="deepseek-r1-distill-llama-70b")

#Step2: Retrieve Docs

# def retrieve_docs(query):
#     return faiss_db.similarity_search(query)

# def get_context(documents):
#     context = "\n\n".join([doc.page_content for doc in documents])
#     return context
def retrieve_docs(query, top_k=3):
    query_embedding = embeddings.embed_query(query)

    # Fetch all documents from MongoDB
    results = collection.find({})
    scored_results = []
    
    for doc in results:
        stored_embedding = np.array(doc["embedding"])
        score = np.dot(query_embedding, stored_embedding)  # Cosine similarity

        scored_results.append((doc["text"], score))

    # Sort results by similarity score (highest first)
    scored_results.sort(key=lambda x: x[1], reverse=True)

    retrieved_texts = [text for text, _ in scored_results[:top_k]]

    if not retrieved_texts:
        print("⚠️ No relevant documents found in MongoDB.")

    return retrieved_texts

def get_context(documents):
    # Since ⁠ retrieve_docs() ⁠ returns a list of strings, no need for ⁠ .page_content ⁠
    context = "\n\n".join(documents)  # Joining text chunks as context
    return context


#Step3: Answer Question

custom_prompt_template = """
You are a debt management advisor. Use the pieces of information provided in the context to answer user's question.
If you dont know the answer, just say that you dont know, dont try to make up an answer. 
Analyze the income and debt data provided by the user and suggest the best way to payoff the debt and how to prioritize the repayment of different debts.
Calculate the amount saved by providing the best strategy to payoff the debt. Answer the question in a detailed manner. Do not use the $ symbol while generating the response.
Question: {question} 
Context: {context} 
Income: 4000 dollars per month
Essential Expenses: 2000 dollars per month
Non-Essential Expenses: 1000 dollars per month
Debt 1: 10000 dollars(Credit Card)
Debt 2: 5000 dollars(Student Loan)
Debt 3: 3000 dollars(Car Loan)
APR1: 18%
APR2: 6%
APR3: 5%
Duration1: 12 months
Duration2: 10 years
Duration3: 5 years
Answer:
"""

def answer_query(documents, model, query):
    context = get_context(documents)
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | model
    return chain.invoke({"question": query, "context": context})

#question="If a government forbids the right to assemble peacefully which articles are violated and why?"
#retrieved_docs=retrieve_docs(question)
#print("AI Lawyer: ",answer_query(documents=retrieved_docs, model=llm_model, query=question))