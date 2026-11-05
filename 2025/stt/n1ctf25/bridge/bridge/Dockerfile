FROM rust:1.90-slim-trixie AS build

RUN apt-get update -y && apt-get install -y pkg-config libudev-dev libssl-dev

ENV OPENSSL_NO_VENDOR=1

COPY ./server /app/server
COPY ./challenge /app/challenge

WORKDIR /app/server

RUN cargo build --release && cp target/release/server /app/run && cargo clean

FROM debian:trixie-slim

RUN apt-get update -y && apt-get install -y tini
ENTRYPOINT ["tini", "--"]

COPY --from=build /app/run /app/run
COPY ./challenge.so /app/challenge.so
WORKDIR /app

CMD ["/app/run"]