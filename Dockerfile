FROM python:3

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY scrape.py /

RUN mkdir /app
WORKDIR /app

ENTRYPOINT ["/scrape.py"]
