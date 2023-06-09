#!/usr/bin/env bash

git pull origin main

docker-compose run --entrypoint=/scrape.py scraper

if [ ! -z "$(git status --porcelain=v1 2>/dev/null)" ]; then
  git add .
  git commit -m "Automated commit"
  git push origin main
fi
