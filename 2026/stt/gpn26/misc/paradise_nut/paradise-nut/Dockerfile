# docker build -t paradise-nut . && docker run -p 1337:1337 --rm -it paradise-nut
FROM ubuntu:26.04@sha256:5e275723f82c67e387ba9e3c24baa0abdcb268917f276a0561c97bef9450d0b4

# install socat
RUN apt-get update -y && apt-get install socat -y --no-install-recommends \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

ARG FLAG=GPNCTF{fake_flag}
RUN echo "$FLAG" > /flag
RUN chmod 400 /flag         # only root can read /flag
RUN chmod u+s /usr/bin/nl   # run `nl /flag` to win

RUN useradd user
USER user
COPY pnut-sh.sh chal.sh ./
EXPOSE 1337
ENTRYPOINT [ "socat", "tcp-l:1337,reuseaddr,fork", "EXEC:./chal.sh,stderr" ]

