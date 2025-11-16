FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .
    
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]