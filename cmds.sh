#!/usr/bin/env bash

curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ "email": "hakan@debian.org", "password": "pass"  }' 'http://0.0.0.0:8000/v1/login_password'
curl -H 'Authorization: Bearer z8XT5jpnmHgEo66nSctLJzRRpvTuhuOdDmNmp3+BU3I' 'http://0.0.0.0:8000/v1/record'
