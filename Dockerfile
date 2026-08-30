FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN pip install --no-cache-dir uv==0.12.5 \
    && uv sync --locked --no-dev

COPY aak ./aak

USER 65532:65532
EXPOSE 8080
CMD ["python", "-m", "aak.cloud_run"]
