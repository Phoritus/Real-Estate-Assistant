from env import GROQ_API_KEY
from uuid import uuid4

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not set in environment variables.")

from langchain_classic.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain_community.document_loaders import WebBaseLoader
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, HttpUrl
from typing import List
from fastapi import HTTPException


# --- Pydantic Models for API Request/Response ---

class UrlList(BaseModel):
    urls: List[HttpUrl]

class Query(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: str

# --- Global Variables ---

llm = None
embeddings = None
vector_store = None

# --- Component Initialization Functions ---

def initialize_component():
    global llm, embeddings, vector_store

    print("Initial LLM")
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        max_tokens=2048,
    )
    print("Initialized LLM")

    print("Initial Embeddings")
    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-large",
        model_kwargs={"trust_remote_code": True},
    )
    print("Initialized Embeddings")

    print("Initial Chroma Vector Store")
    vector_store = Chroma(
        collection_name="real_estate_documents",
        embedding_function=embeddings,
        persist_directory="../chroma_db",
    )
    print("Initialized Chroma Vector Store")


def process_url(url_list: List[str]):
    if embeddings is None or vector_store is None:
        print("Components not initialized. Please call initialize_component() first.")
        raise Exception("Components not initialized.")

    loader = WebBaseLoader(url_list)
    documents = loader.load()

    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "],
        chunk_size=1000,
        chunk_overlap=200,
    )
    docs = text_splitter.split_documents(documents)
    print(f"Documents split completed. Found {len(docs)} chunks.")

    print("Adding documents to vector store...")
    uid = [str(uuid4()) for _ in range(len(docs))]

    vector_store.add_documents(
        documents=docs,
        ids=uid
    )
    print(f"Documents added to vector store. Total documents: {vector_store._collection.count()}")
    return len(docs)


def generate_answer(query: str):
    if vector_store is None or llm is None:
        raise Exception("Vector store or LLM is not initialized.")

    print("RetrievalQAWithSourcesChain processing...")
    chain = RetrievalQAWithSourcesChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        return_source_documents=True,
    )

    print("Generating answer...")
    result = chain.invoke({"question": query})
    print("Answer generated.")

    sources_output = result.get("sources", "No sources found")
    if isinstance(sources_output, list):
         sources_output = ", ".join(list(set(doc.metadata.get("source", "Unknown") for doc in sources_output)))

    return result.get("answer", "No answer found"), sources_output
  

def initialize_process():
    """
    Initialize the components (LLM, embeddings, and vector store).
    This should be called once before using other endpoints.
    """
    try:
        initialize_component()
        return {"message": "Components initialized successfully."}
    except Exception as e:
        print(f"Error initializing components: {e}")
        raise HTTPException(status_code=500, detail=f"Error initializing components: {str(e)}")
      
def process_urls(payload: UrlList):
    """
    Accept a list of URLs, process each URL to extract text,
    split into chunks, generate embeddings, and store in Vector Store.
    """
    try:
        # Convert URLs to strings
        url_strings = [str(url) for url in payload.urls]
        num_chunks = process_url(url_strings)
        return {
            "message": f"Successfully processed {len(url_strings)} URLs.",
            "chunks_added": num_chunks
        }
    except Exception as e:
        print(f"Error processing URLs: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing URLs: {str(e)}")
      
def get_answer(payload: Query):
    """
    Accept a question string, retrieve relevant documents from Vector Store,
    and generate an answer using the LLM along with source references.
    """
    try:
        answer, sources = generate_answer(payload.question)
        return AnswerResponse(answer=answer, sources=sources)
    except Exception as e:
        print(f"Error generating answer: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")