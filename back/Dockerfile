# Stage 1: Build virtual environment
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Montar caches para acelerar las descargas e instalar dependencias congeladas
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime image
FROM python:3.11-alpine

WORKDIR /app

# Copiar el entorno virtual construido
COPY --from=builder /app/.venv /app/.venv
# Copiar el código fuente
COPY . /app

# Configurar variables de entorno indispensables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Ejecutar usando la fábrica de la app
CMD ["python", "src/presentation/app.py"]
