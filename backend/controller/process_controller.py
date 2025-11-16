from env import GROQ_API_KEY, CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE
from uuid import uuid4

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not set in environment variables.")

from langchain_community.document_loaders import WebBaseLoader
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
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
    answer: str | list[str]
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
        model_name="intfloat/multilingual-e5-small"
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
    raw_docs = (qres.get("documents") or [[]])[0] if qres else []
    metadatas = (qres.get("metadatas") or [[]])[0] if qres else []

    # Normalize documents into a flat list of strings
    docs_texts: list[str] = []
    for d in raw_docs:
        if d is None:
            continue
        if isinstance(d, (list, tuple)):
            for x in d:
                if x is not None:
                    docs_texts.append(str(x))
        else:
            docs_texts.append(str(d))

    context = "\n\n".join(docs_texts)
    # Build a proper chat prompt; from_template expects a string, not a list
    # Use from_messages with role-tagged templates and align variable names
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful real estate analysis assistant."),
        (
            "user",
            "Answer the user's question only using the context. If the answer is not in the context, say you don't know.\n\n"
            "Context:\n{context}\n\nQuestion: {question}\nAnswer:",
        ),
    ])
    print("Generating answer with LLM...")
    chain = prompt | llm
    llm_result = chain.invoke({"context": context, "question": query})
    # Extract content depending on return type (handle BaseMessage, dict, list)
    try:
        from langchain_core.messages import BaseMessage  # lazy import, avoids hard dependency at module import time
    except Exception:
        BaseMessage = tuple()  # type: ignore

    if isinstance(llm_result, str):
        answer_text = llm_result
    elif isinstance(llm_result, BaseMessage):  # type: ignore[arg-type]
        content = getattr(llm_result, "content", "")
        if isinstance(content, list):
            answer_text = " ".join(str(x) for x in content)
        else:
            answer_text = str(content)
    elif isinstance(llm_result, dict):
        if "text" in llm_result:
            answer_text = str(llm_result.get("text", ""))
        elif "content" in llm_result:
            ct = llm_result.get("content", "")
            if isinstance(ct, list):
                answer_text = " ".join(str(x) for x in ct)
            else:
                answer_text = str(ct)
        else:
            answer_text = str(llm_result)
    elif isinstance(llm_result, (list, tuple)):
        answer_text = " ".join(str(x) for x in llm_result)
    else:
        answer_text = str(llm_result)

    # Sanitize answer text
    for token in ("SOURCES:", "Sources:", "Source:"):
        idx = answer_text.find(token)
        if idx != -1:
            answer_text = answer_text[:idx].strip()
            break
    answer_text = re.sub(r"^\s*(FINAL\s+ANSWER:|Final\s+Answer:|Answer:)\s*", "", answer_text, flags=re.IGNORECASE)

    # Build sources from metadatas (normalize to strings)
    source_items: list[str] = []
    for md in metadatas or []:
        if not isinstance(md, dict):
            # If metadata comes nested or as other types, coerce to string
            source_items.append(str(md))
            continue
        src = md.get("source") or md.get("url") or None
        if src is None:
            continue
        if isinstance(src, (list, tuple)):
            for s in src:
                if s:
                    source_items.append(str(s))
        else:
            source_items.append(str(src))
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for s in source_items:
        if s not in seen:
            seen.add(s)
            deduped.append(s)
    sources_output = ", ".join(deduped) if deduped else "No sources found"

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