FROM rust:1.95-bullseye AS build

COPY . /challenge
WORKDIR /challenge

RUN cargo build --release

FROM debian:bullseye AS flag

ARG Flag "GPNCTF{dummyflag}"
RUN echo ${Flag} > /flag

FROM debian:bullseye AS challenge
RUN useradd -m -u 1000 -s /bin/bash ctf
RUN apt update && apt install socat -y && apt clean

COPY --from=build --chown=root:root --chmod=4755 /challenge/target/release/supercat /usr/local/bin/supercat

COPY --from=flag --chown=root:root --chmod=0400 /flag /flag

USER ctf
WORKDIR /home/ctf
EXPOSE 1337

ENTRYPOINT ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:bash"]
