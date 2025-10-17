FROM python:3.14.0-alpine

WORKDIR /app

COPY PyPtt/ /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn fastapi

# uvicorn app:api_server --host 0.0.0.0 --port 8787
EXPOSE 8787
CMD ["uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8787"]
