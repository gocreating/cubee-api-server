# modified from https://xbuba.com/questions/46711990
# it is the only working version for installing `psycopg2`
FROM alpine:3.7

ARG COMMIT_REF
ARG BUILD_DATE

COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache python3 postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    python3 -m pip install -r /tmp/requirements.txt --no-cache-dir && \
    apk --purge del .build-deps && \
    rm /tmp/requirements.txt

COPY . /srv/cubee-api-server

WORKDIR /srv/cubee-api-server

ENV APP_COMMIT_REF=${COMMIT_REF} \
    APP_BUILD_DATE=${BUILD_DATE}

EXPOSE 8000

ENTRYPOINT ["sh", "/srv/cubee-api-server/docker-entrypoint.sh"]
