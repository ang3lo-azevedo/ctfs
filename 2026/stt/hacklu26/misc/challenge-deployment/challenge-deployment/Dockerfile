FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp

RUN pip install --no-cache-dir flask kubernetes requests pyyaml

# kubectl (used by the controller).
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
 && kv="$(curl -fsSL https://dl.k8s.io/release/stable.txt)" \
 && curl -fsSL -o /usr/local/bin/kubectl \
      "https://dl.k8s.io/release/${kv}/bin/linux/$(dpkg --print-architecture)/kubectl" \
 && chmod 0755 /usr/local/bin/kubectl \
 && apt-get purge -y --auto-remove curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY common.py controller.py api.py ui.py ./
COPY images.png ./

# command (python controller.py | api.py | ui.py); controller is the default.
USER 10001:10001
EXPOSE 8080
CMD ["python", "controller.py"]
