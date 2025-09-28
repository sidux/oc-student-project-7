# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

WORKDIR /srv/app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

ENV PATH="/srv/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
