FROM python:3.13-slim

# docker build -t fruit-market .
# docker run --rm -p 5000:5000 fruit-market

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && curl -fsSL https://github.com/foundry-rs/foundry/releases/download/v1.7.1/foundry_v1.7.1_linux_amd64.tar.gz \
    | tar -xz -C /usr/local/bin forge cast anvil chisel

RUN mkdir /app
COPY python/ /app/python
COPY html/ /app/html
COPY eth/ /app/eth
COPY start.sh /app/

WORKDIR /app/python
RUN pip3 install --no-cache-dir -r requirements.txt
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
