#!/usr/bin/env bash
set -e
docker build . -t hakanardo/facetree
docker run --rm -ti hakanardo/facetree python test.py
docker push hakanardo/facetree
