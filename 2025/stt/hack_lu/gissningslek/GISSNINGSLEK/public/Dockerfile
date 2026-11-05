FROM debian:bookworm-slim@sha256:b1a741487078b369e78119849663d7f1a5341ef2768798f7b7406c4240f86aef

COPY docker-stuff/ynetd /sbin/ynetd
COPY docker-stuff/readflag /readflag
COPY flag.txt /flag.txt

RUN chown root:root /readflag /flag.txt && \
    chmod  500 /sbin/ynetd && \
    chmod 2555 /readflag   && \
    chmod  040 /flag.txt

WORKDIR /app
COPY gissningslek.sh /app/gissningslek.sh

RUN useradd --no-create-home --shell /bin/bash ctf
USER ctf
RUN ! find / -writable -or -user "$(id -un)" -or -group $(id -Gn | sed -e 's/ / -or -group /g') 2> /dev/null | grep -Ev -m 1 '^(/dev/|/proc/|/sys/|/tmp|/var/tmp|/run/lock|/var/lock)'
USER root
RUN find / -ignore_readdir_race -type f \( -perm -4000 -o -perm -2000 \) -not -wholename /readflag -delete

CMD ynetd -lt 240 -d /app -sh y -se y -np y '/app/gissningslek.sh'
