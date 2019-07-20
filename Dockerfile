FROM python:3.7.4-slim

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt \
    && apt-get autoclean \
    && apt-get clean

COPY . /srv/cubee-api-server

WORKDIR /srv/cubee-api-server

EXPOSE 8000

ENTRYPOINT ["/srv/cubee-api-server/docker-entrypoint.sh"]
