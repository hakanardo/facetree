#!/usr/bin/env bash
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ "email": "hakan@debian.org", "password": "7tsLKBZo"  }' 'http://0.0.0.0:8000/v1/users/login/password'
curl -X POST -H 'Authorization: Bearer SNyBsTTqghz6kGsUwl2b8YIyqwgjz893hCu80sM1xOU' --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ "email": "hakan@debian.org", "individual": "xxx"  }' 'http://0.0.0.0:8000/v1/users/invite'
curl -H 'Authorization: Bearer SNyBsTTqghz6kGsUwl2b8YIyqwgjz893hCu80sM1xOU' 'http://0.0.0.0:8000/v1/records'
curl -X POST -H 'Authorization: Bearer SNyBsTTqghz6kGsUwl2b8YIyqwgjz893hCu80sM1xOU' --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ "old": "i6WQ6SwQ", "new": "pass"  }' 'http://0.0.0.0:8000/v1/users/password'
