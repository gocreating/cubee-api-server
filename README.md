# Cubee API Server

## Launch in different environments

### (Recommended) dev/stg in container

``` bash
$ docker-compose up [-d]
```

### prod in container

``` bash
docker-compose -f ./docker-compose-prod.yaml up
```

### dev/stg in host os

``` bashh
$ CONFIG_PATH="./config-stg.yaml" FLASK_APP=app FLASK_ENV=development flask run
```

### Initialize database

``` bash
$ docker-compose run api-server init-db
$ docker-compose -f ./docker-compose-prod.yaml run --entrypoint flask api-server init-db
```

## Encryption/Decryption Sensitive File with Ansible-Vault

1. Build ansible image

``` bash
$ docker build -t gocreating/ansible-vault -f ansible-vault-dockerfile .
```

2. Encrypt/Decrypt

``` bash
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault encrypt ./configMap-prod.yaml
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault encrypt ./configMap-stg.yaml
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault decrypt ./configMap-prod.yaml
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault decrypt ./configMap-stg.yaml
```

## Touble Shooting

### Docker Compose Error

``` bash
$ docker-compose up
ERROR: readlink /var/lib/docker/overlay2: invalid argument
```

Solution

``` bash
$ docker-compose build --no-cache
```

### Docker Compose Port Forwarding Not Work

Make sure the flask app binds host `0.0.0.0`, ex:

``` bash
$ flask run --host=0.0.0.0
```

### GKE上的pod連不到external database

Attach到container上，打request後看log，發現DNS server有問題

``` bash
$ kubectl attach cubee-api-server-7d6cdc977-m2z6r [-c cubee-api-server]
If you don't see a command prompt, try pressing enter.
[2019-07-27 13:34:38,034] ERROR in auth: (psycopg2.OperationalError) could not translate host name "bwso4xjnayfic4zdqzkn-postgresql.services.clever-cloud.com" to address: Try again

(Background on this error at: http://sqlalche.me/e/e3q8)
```

想辦法釋放資源，讓k8s的dns pod可以啟動，例如調整node數量，調整完查看一下DNS

``` bash
$ nslookup bwso4xjnayfic4zdqzkn-postgresql.services.clever-cloud.com
Server:         169.254.169.254
Address:        169.254.169.254#53

Non-authoritative answer:
bwso4xjnayfic4zdqzkn-postgresql.services.clever-cloud.com       canonical name = postgresql-c4.services.clever-cloud.com.
Name:   postgresql-c4.services.clever-cloud.com
Address: 185.42.117.114
```
