#!/bin/bash
#docker buildx build -f Dockerfile.build --output type=local,dest=. .
docker build -f Dockerfile.build --output=. .
