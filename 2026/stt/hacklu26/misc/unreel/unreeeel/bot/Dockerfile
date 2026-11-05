FROM node:22.23.4-bookworm-slim@sha256:de170b39439eb0e5a3444ad7d60b015614a381e10fecae2e30ec9e735122f38d

RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium ca-certificates fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

# Block the compromised eMudhra keys without requiring CRLSet downloads.
COPY chromium-emudhra.json /etc/chromium/policies/managed/unreel-emudhra.json

ENV PUPPETEER_SKIP_DOWNLOAD=1
ENV CHROMIUM_PATH=/usr/bin/chromium

WORKDIR /bot
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY bot.js ./

USER node
EXPOSE 8080
CMD ["node", "bot.js"]
