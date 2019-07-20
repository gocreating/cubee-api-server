FROM python:3.7.4-slim

ARG COMMIT_REF
ARG BUILD_DATE

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt \
    && apt-get autoclean \
    && apt-get clean

COPY . /srv/cubee-api-server

WORKDIR /srv/cubee-api-server

ENV APP_COMMIT_REF=${COMMIT_REF} \
    APP_BUILD_DATE=${BUILD_DATE}

EXPOSE 8000

ENTRYPOINT ["sh", "/srv/cubee-api-server/docker-entrypoint.sh"]
