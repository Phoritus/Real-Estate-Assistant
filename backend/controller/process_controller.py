from env import GROQ_API_KEY, CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE
from uuid import uuid4

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not set in environment variables.")

from langchain_community.document_loaders import WebBaseLoader
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, HttpUrl
from typing import List
import re
from fastapi import HTTPException
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.CloudClient(
  api_key=CHROMA_API_KEY,
  tenant=CHROMA_TENANT,
  database=CHROMA_DATABASE
)

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
client = None

# --- Component Initialization Functions ---

def initialize_component():
    global llm, embeddings, vector_store, client

    print("Initial LLM")
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        max_tokens=2048,
    )
    print("Initialized LLM")

    print("Initial Embeddings Function (Chroma)")
    # Use Chroma's embedding function compatible with Cloud collections
    embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="intfloat/multilingual-e5-large"
    )
    print("Initialized Embeddings Function")

    # Initialize Chroma Cloud client lazily to avoid import-time env errors
    if not (CHROMA_API_KEY and CHROMA_TENANT and CHROMA_DATABASE):
        raise Exception("Chroma Cloud environment variables are not configured.")
    print("Initial Chroma Cloud Collection")
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
    )
    vector_store = client.get_or_create_collection(
        name="real_estate_documents",
        embedding_function=embeddings,
    )
    print("Initialized Chroma Cloud Collection")



def process_single_url(url: str) -> int:
    """
    Process a single URL: load, split, embed, and store in the vector store.
    Returns the number of chunks added for this URL.
    """
    if embeddings is None or vector_store is None:
        print("Components not initialized. Please call initialize_component() first.")
        raise Exception("Components not initialized.")

    loader = WebBaseLoader([url])
    documents = loader.load()

    print(f"Splitting documents for URL: {url} ...")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "],
        chunk_size=1000,
        chunk_overlap=200,
    )
    docs = text_splitter.split_documents(documents)
    print(f"URL {url} split completed. Found {len(docs)} chunks.")

    print(f"Adding {len(docs)} chunks to vector store for URL: {url} ...")
    uid = [str(uuid4()) for _ in range(len(docs))]

    # Upsert raw texts and metadatas into Chroma Cloud
    vector_store.upsert(
        documents=[d.page_content for d in docs],
        metadatas=[d.metadata for d in docs],
        ids=uid,
    )
    try:
        total = vector_store.count()
    except Exception:
        total = 'unknown'
    print(f"Done adding for URL {url}. Total documents: {total}")
    return len(docs)


def generate_answer(query: str):
    if vector_store is None or llm is None:
        raise Exception("Vector store or LLM is not initialized.")

    print("Querying Chroma for top documents...")
    qres = vector_store.query(query_texts=[query], n_results=5)
    # Results are lists per query; we used a single query so index 0
    docs_texts = qres.get("documents", [[]])[0] if qres else []
    metadatas = qres.get("metadatas", [[]])[0] if qres else []

    context = "\n\n".join(docs_texts)
    prompt = (
        "You are a helpful real estate analysis assistant. "
        "Answer the user's question only using the context. "
        "If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        "Answer:"
    )

    print("Generating answer with LLM...")
    llm_result = llm.invoke(prompt)
    # Extract content depending on return type
    if isinstance(llm_result, str):
        answer_text = llm_result
    else:
        # LangChain ChatGroq returns a BaseMessage with .content
        answer_text = getattr(llm_result, "content", str(llm_result))

    # Sanitize answer text
    for token in ("SOURCES:", "Sources:", "Source:"):
        idx = answer_text.find(token)
        if idx != -1:
            answer_text = answer_text[:idx].strip()
            break
    answer_text = re.sub(r"^\s*(FINAL\s+ANSWER:|Final\s+Answer:|Answer:)\s*", "", answer_text, flags=re.IGNORECASE)

    # Build sources from metadatas
    sources_set = []
    for md in metadatas:
        src = md.get("source") or md.get("url") or "Unknown"
        if src not in sources_set:
            sources_set.append(src)
    sources_output = ", ".join(sources_set) if sources_set else "No sources found"

    print("Answer generated.")
    return answer_text, sources_output
  

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
    Processes URLs individually to continue on errors and report per-URL results.
    """
    # Convert URLs to strings
    url_strings = [str(url) for url in payload.urls]

    total_chunks = 0
    successes = []  # list of {url, chunks}
    failures = []   # list of {url, error}

    for url in url_strings:
        try:
            chunks = process_single_url(url)
            total_chunks += chunks
            successes.append({"url": url, "chunks": chunks})
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            failures.append({"url": url, "error": str(e)})

    message = (
        f"Processed {len(url_strings)} URLs. "
        f"Success: {len(successes)}, Failed: {len(failures)}."
    )

    # Maintain backward-compatible key 'chunks_added' while adding details
    return {
        "message": message,
        "chunks_added": total_chunks,
        "total_chunks": total_chunks,
        "details": {
            "success": successes,
            "failed": failures,
        },
    }
      
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