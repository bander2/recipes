#!/usr/bin/env python

import pandas as pd
import os
import re

import recipe_scrapers._exceptions
import yaml
import urllib.request
import shutil
from datetime import datetime
from slugify import slugify
from recipe_scrapers import scrape_me
from pathlib import Path


class Recipe:
    def __init__(self, url: str, content_dir: str):
        self.url = url
        self.content_dir = content_dir

    def exists(self) -> bool:
        """Check to see if this recipe already exists."""
        for path in Path(self.content_dir).rglob('index.md'):
            with open(path) as file:
                docs = yaml.safe_load_all(file)
                if next(docs)['canonicalUrl'] == self.url:
                    return True

        return False

    def handle_image(self, url: str, slug: str):
        """Save the image."""
        dir = os.path.join(self.content_dir, slug, 'images')
        os.mkdir(dir)

        try:
            urllib.request.urlretrieve(url, os.path.join(dir, 'thumbnail.jpg'))
        except:
            Path(dir).rmdir()
            return False

        return True

    def snake_keys(self, data: dict):
        """
        Take a dict with camel case keys and convert them to snake case because
        hugo does not support camel case keys.
        """
        snake = {}
        for key, value in data.items():
            snake.update({re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower(): value})
        return snake

    def write(self) -> bool:
        if self.exists():
            return False

        try:
            scraper = scrape_me(self.url, wild_mode=True)
        except:
            print("Cannot scrape " + self.url)
            return False

        slug = slugify(scraper.title())
        os.mkdir(os.path.join(self.content_dir, slug))

        frontmatter = dict(
            title = scraper.title(),
            date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            draft = False,
            host = scraper.host(),
            canonicalUrl = self.url,
            ingredients = scraper.ingredients(),
            directions = scraper.instructions_list(),
        )

        try:
            frontmatter.update({'yields': scraper.yields()})
        except:
            pass

        try:
            frontmatter.update({'nutrients': scraper.nutrients()})
        except:
            pass

        if scraper.image() and self.handle_image(scraper.image(), slug):
            frontmatter.update({'resources': dict(
                name='thumbnail',
                src='images/thumbnail.jpg'
            )})

        content = "---\n" + yaml.dump(frontmatter) + "---\n"
        f = open(os.path.join(self.content_dir, slug, 'index.md'), 'a')
        f.write(content)
        f.close()

        return True


class Application:
    def __init__(self, content_dir: str, urls: list):
        self.content_dir = content_dir
        self.urls = urls

    def add_new(self) -> bool:
        """Add new recipes."""
        updated = False
        for url in self.urls:
            recipe = Recipe(url, self.content_dir)
            if recipe.write():
                updated = True
        return updated

    def delete_old(self) -> bool:
        """Remove local recipes that are not in the list of urls."""
        updated = False
        for path in Path(content_dir).rglob('index.md'):
            with open(path) as file:
                docs = yaml.safe_load_all(file)
                this_url = next(docs)['canonicalUrl']
                if this_url and not this_url in data[0].values:
                    shutil.rmtree(os.path.dirname(path))
                    updated = True
        return updated

    def run(self):
        self.add_new()
        self.delete_old()

content_dir = '/app/content/recipe'
data = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_W1hoW_XLMMd2jEFuFuEuIKZkGKwuNjWWknJfBzGZpe7C08G5FEKAS4uCT7iWdQOzzBQXJqoj3Wyq/pub?output=csv', header=None)

for url in data[0]:
    recipe = Recipe(url, content_dir)
    recipe.write()
