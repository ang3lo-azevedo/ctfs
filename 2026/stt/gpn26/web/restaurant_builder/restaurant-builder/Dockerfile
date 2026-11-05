FROM scratch AS handout

COPY Dockerfile /handout/
COPY src/main.py src/pyproject.toml src/uv.lock /handout/src/

#-----------------------------------------

# docker build -t restaurant-builder .
# docker run --rm -p 1337:1337 -e FLAG="GPNCTF{this_is_a_dummy_flag}" restaurant-builder
# then connect to http://localhost:1337
FROM ghcr.io/astral-sh/uv:alpine AS challenge

COPY src/.python-version src/pyproject.toml src/uv.lock app/
WORKDIR /app
RUN uv sync

COPY src/ /app

EXPOSE 1337
ENTRYPOINT ["uv", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--workers", "1", "--bind", "0.0.0.0:1337"]
