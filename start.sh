#!/usr/bin/env bash
docker run --rm -it -p 8080:80 -v $(pwd):/app hakanardo/facetree