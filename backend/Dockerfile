FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 8001

# Use $PORT environment variable if provided (for Railway), otherwise default to 8001
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
