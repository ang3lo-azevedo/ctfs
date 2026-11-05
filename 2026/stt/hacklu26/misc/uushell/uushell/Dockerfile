FROM debian:bookworm-slim
RUN apt update && apt install -y sharutils socat
COPY --chown=nobody --chmod=000 flag.txt /flag
USER nobody
CMD ["socat", "tcp-l:1337", "system:uuencode x | sed -n 2p | sh"]
