# Dockerfile

# pull the official docker image
FROM python:3.11.6-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src

ENV PYTHONPATH=/app
EXPOSE 8080
CMD ["uvicorn", "src.fauth.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
