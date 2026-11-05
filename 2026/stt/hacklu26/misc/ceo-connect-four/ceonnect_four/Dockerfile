FROM debian:trixie-20260925-slim@sha256:a99cfc517144bc59b1978475ec53b46ecabec7e43635402ee5b77cc54cd1b20a

RUN useradd -m -d /chal ctf && \
    chown -R root:root /chal && \
    chmod +rx /chal
WORKDIR /chal

COPY entrypoint.sh /
COPY ynetd c4 .

EXPOSE 1024
CMD ["/entrypoint.sh"]
