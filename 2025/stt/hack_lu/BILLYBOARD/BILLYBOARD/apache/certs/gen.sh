#!/usr/bin/env bash
set -e

CN="apache"
CA_KEY=local_rootCA.key
CA_CRT=local_rootCA.crt
APP_KEY=local.key
APP_CRT=local.crt
APP_PEM=local.pem

# make CA if not exists
openssl req -x509 -newkey rsa:2048 -days 3650 -nodes \
  -subj "/CN=Local Dev CA" -keyout $CA_KEY -out $CA_CRT

# make server key + csr + signed cert
openssl req -newkey rsa:2048 -nodes -keyout $APP_KEY -out local.csr \
  -subj "/CN=$CN"
echo "subjectAltName=DNS:$CN" > local.ext
openssl x509 -req -in local.csr -CA $CA_CRT -CAkey $CA_KEY -CAcreateserial \
  -out $APP_CRT -days 365 -sha256 -extfile local.ext
cat $APP_CRT $CA_CRT > $APP_PEM

rm local.csr local.ext local.crt local_rootCA.srl local_rootCA.key

echo "The real server uses VALID letsencrypt certs !!!!"
