FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=1337

COPY agents ./agents
COPY game.py server.py ./ 

RUN useradd --create-home --system ctf
USER ctf

EXPOSE 1337

CMD ["python", "server.py"]
