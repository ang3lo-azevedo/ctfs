FROM ubuntu:latest

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y cmus ca-certificates

RUN useradd -m -s /bin/bash ctf

COPY --chown=root:root --chmod=0755 readflag /readflag
RUN chmod +s /readflag
COPY --chown=root:root --chmod=0400 flag.txt /flag.txt

COPY --chown=ctf:ctf cmus/ /home/ctf/.config/cmus/
COPY --chown=ctf:ctf music/ /home/ctf/Music/

RUN mkdir -p /home/ctf/.config/cmus/playlists && \
    find /home/ctf/Music -type f ! -name '.*' | sort > /home/ctf/.config/cmus/playlists/all

USER ctf
WORKDIR /home/ctf

ENV TERM=xterm-256color

EXPOSE 1024
ENTRYPOINT ["script", "-q", "-e", "-f", "-c", "cmus --listen 0.0.0.0:1024", "/dev/null"]
