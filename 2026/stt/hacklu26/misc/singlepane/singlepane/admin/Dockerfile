FROM debian:sid-slim@sha256:fb75970a5ba2a81ca409ed0cabcf05d53e058086fd397f7a63943ded5bd15f84 AS build

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates gcc git libc6-dev tmux=3.8-1

# helper that reads the flag
COPY readflag.c /
RUN gcc -O2 -s -o /readflag /readflag.c

# let tpm install the plugins
COPY tmux.conf /root/.tmux.conf
RUN git clone -q https://github.com/tmux-plugins/tpm /root/.tmux/plugins/tpm \
 && ~/.tmux/plugins/tpm/bin/install_plugins


FROM debian:sid-slim@sha256:fb75970a5ba2a81ca409ed0cabcf05d53e058086fd397f7a63943ded5bd15f84

RUN apt-get update \
 && apt-get install -y --no-install-recommends tmux=3.8-1 procps \
 && [ "$(tmux -V)" = "tmux 3.8" ] \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m op && mkdir -p /srv/pub && chown op:op /srv/pub

COPY --from=build --chmod=4755 /readflag /usr/local/bin/readflag

COPY --from=build --chown=op:op /root/.tmux /home/op/.tmux
COPY --chown=op:op tmux.conf /home/op/.tmux.conf
COPY --chmod=0755 entrypoint.sh /

USER op
ENV TERM=xterm-256color
ENTRYPOINT ["/entrypoint.sh"]
