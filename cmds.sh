#!/usr/bin/env bash

curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ "email": "hakan@debian.org", "individual": "xxx"  }' 'http://0.0.0.0:8000/v1/users/invite'
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ "email": "hakan@debian.org", "password": "7tsLKBZo"  }' 'http://0.0.0.0:8000/v1/users/login_password'
curl -H 'Authorization: Bearer SNyBsTTqghz6kGsUwl2b8YIyqwgjz893hCu80sM1xOU' 'http://0.0.0.0:8000/v1/records'
