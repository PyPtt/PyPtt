FROM python:3.14.0-alpine

WORKDIR /app

COPY pyproject.toml setup.py ./
COPY PyPtt/ ./PyPtt/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .[api]

# uvicorn PyPtt.api_server:app --host 0.0.0.0 --port 8787
EXPOSE 8787
CMD ["uvicorn", "PyPtt.api_server:app", "--host", "0.0.0.0", "--port", "8787"]
