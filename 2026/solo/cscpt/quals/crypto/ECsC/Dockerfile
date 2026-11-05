FROM python:3.12-slim

WORKDIR /app

COPY server.py /app/server.py

EXPOSE 1337

CMD ["python3", "/app/server.py"]

# docker build -t ecsc  .
# docker run --rm -p 1337:1337 ecsc