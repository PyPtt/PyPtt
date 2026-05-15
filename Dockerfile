FROM python:3.14.0-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml setup.py README.md ./
COPY PyPtt/ ./PyPtt/

RUN pip install --upgrade pip && \
    pip install '.[api]'

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# uvicorn PyPtt.api_server:app --host 0.0.0.0 --port 8787
EXPOSE 8787
CMD ["uvicorn", "PyPtt.api_server:app", "--host", "0.0.0.0", "--port", "8787"]
