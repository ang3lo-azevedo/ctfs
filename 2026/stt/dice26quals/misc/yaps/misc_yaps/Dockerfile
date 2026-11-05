FROM python:3.15-rc AS app

# Set up working directory
WORKDIR /app

# Copy the challenge files
COPY scanner.py /app/scanner.py
COPY server.py /app/run
COPY flag.txt /app/flag.txt

# Make server executable
RUN chmod 755 /app/run && chmod 644 /app/flag.txt /app/scanner.py

FROM pwn.red/jail
COPY --from=app / /srv
ENV JAIL_MEM=512M JAIL_TIME=30 JAIL_PIDS=20 JAIL_POW=30000
