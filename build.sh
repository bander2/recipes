#!/usr/bin/env bash

docker-compose run --entrypoint=/scrape.py scraper

if ! git diff-index --quiet HEAD --
then
  git add .
  git commit -m "Automated commit"
  git push origin main
fi
