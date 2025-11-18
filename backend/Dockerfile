FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .
    
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

COPY . .

EXPOSE 8080

ENV USER_AGENT="real-estate-api/1.0"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]