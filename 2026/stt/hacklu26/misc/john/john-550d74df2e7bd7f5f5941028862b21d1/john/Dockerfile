FROM archlinux:base@sha256:b0deabeb3d283da2c7f7dbf0eea051b7b2cd0554e0b737cc457fd21683bdcdd1

ADD --chmod=0755 --checksum=sha256:c125df9762b0c7233459087bb840c0e5dbfc4d9690ee227f1ed8994f4d51d2e0 \
    https://raw.githubusercontent.com/reproducible-containers/repro-sources-list.sh/v0.1.4/repro-sources-list.sh \
    /usr/local/bin/repro-sources-list.sh

RUN --mount=type=cache,target=/var/cache/pacman,sharing=locked \
    /usr/local/bin/repro-sources-list.sh && \
    pacman -Syu --noconfirm --needed \
        john openmpi gunicorn nginx python python-flask util-linux && \
    rm -f /usr/local/bin/repro-sources-list.sh

RUN usermod -d /var/www http
COPY docker-stuff/nginx.conf /etc/nginx/nginx.conf

COPY --chown=0:1337 --chmod=0040 flag.txt /flag.txt
COPY --chown=0:1337 --chmod=2555 docker-stuff/readflag /

COPY app.py /var/www/

RUN chown -R root:root /var/www && \
    find /var/www -type d -exec chmod 555 {} \; && \
    find /var/www -type f -exec chmod 444 {} \; && \
    chown -R root:root /tmp /var/tmp && \
    chmod -R 000 /var/tmp && \
    chmod 1777 /tmp

RUN mkdir --mode=1777 /var/www/.john && \
    mkdir --mode=1777 /var/www/jobs

RUN mkdir -p /var/log/nginx && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

RUN find /usr/lib/systemd /etc/systemd -type l -lname /dev/null -delete 2>/dev/null || true && \
    rm -rf /var/mail /var/spool/mail

USER http
RUN (find --version && id --version && sed --version && grep --version) > /dev/null
RUN ! find / -writable -or -user $(id -un) -or -group $(id -Gn|sed -e 's/ / -or -group /g') 2> /dev/null | grep -Ev -m 1 '^(/dev/|/run/|/proc/|/sys/|/tmp|/var/lock|/var/log/nginx/error.log|/var/log/nginx/access.log|/var/www/.john|/var/www/jobs)'

USER root
RUN find / -ignore_readdir_race -type f \( -perm -4000 -o -perm -2000 \) -not -wholename /readflag -delete

CMD install -d -o http -g http /run/gunicorn; \
    while true; do \
        find /var/www/.john -mindepth 1 -mmin +15 -delete; \
        find /var/www/jobs -mindepth 1 -mmin +15 -delete; \
        find /tmp -mindepth 1 -mmin +15 -user http -delete; \
        sleep 60; \
    done & \
    env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin HOME=/var/www \
        gunicorn --chdir /var/www --user http --group http \
            --workers 2 --threads 4 \
            --bind unix:/run/gunicorn/gunicorn.sock app:app & \
    nginx -g 'daemon off;'
