# modified from https://xbuba.com/questions/46711990
# it is the only working version for installing `psycopg2`
FROM alpine:3.7

ARG PROJECT_REPONAME
ARG SHA1
ARG BUILD_DATE
ARG IMAGE_TAG

COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache python3 postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    python3 -m pip install -r /tmp/requirements.txt --no-cache-dir && \
    apk --purge del .build-deps && \
    rm /tmp/requirements.txt

COPY . /srv/cubee-api-server

WORKDIR /srv/cubee-api-server

ENV repoName=${PROJECT_REPONAME} \
    commitSHA1=${SHA1} \
    buildDate=${BUILD_DATE} \
    imageTag=${IMAGE_TAG}

EXPOSE 8000

ENTRYPOINT ["sh", "/srv/cubee-api-server/docker-entrypoint.sh"]
