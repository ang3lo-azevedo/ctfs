# docker build -t food-inspector .
# docker run -i -t --rm -p 127.0.0.1:1337:1337 -v ./test-flag.txt:/flag food-inspector:latest
FROM ubuntu:25.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    python3 \
    socat

# uv setup
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY app ./frida/frida-portal /app/
COPY main.py .python-version pyproject.toml uv.lock /app/
COPY ./libs /app/libs
COPY entrypoint.sh /app/

WORKDIR /app

RUN uv sync

EXPOSE 1337
ENTRYPOINT ["./entrypoint.sh"]