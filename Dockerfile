FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY knowledge-base ./knowledge-base

RUN useradd --create-home appuser \
    && mkdir -p /home/data/vector-store \
    && chown -R appuser:appuser /home/data
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "uvicorn helpdesk.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
