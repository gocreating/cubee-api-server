# Cubee API Server

## GKE Setup

開機器時storage預設100G，但下限其實可以降到10G

第一次deploy會啟動tiller，所以可能會因為tiller還沒ready，導致deploy失敗

可以打開 cloud console輸入

```
kubectl -n kube-system get po
```

看結果有沒有長得像`tiller-deploy-2654728925-j2zvk`的pod name

如果有，可以rerun看看ci的job

[Helm 部署在 GKE 上的權限問題](https://medium.com/smalltowntechblog/helm-tiller-%E9%83%A8%E7%BD%B2%E5%9C%A8-gke-%E4%B8%8A%E7%9A%84%E6%AC%8A%E9%99%90%E5%95%8F%E9%A1%8C-a016f703372e)

要將`833974311137-compute@developer.gserviceaccount.com`, `Compute Engine default service account` 新增腳色: `Kubernetes Engine 管理`

要將ingress的ip從`臨時`改為`靜態`，給定名字後修改`ingress.yaml`裡的`kubernetes.io/ingress.global-static-ip-name`

- [CircleCI: Persisting Environment Variables Across Steps and Jobs](https://medium.com/@johnthughes/circleci-persisting-environment-variables-across-steps-and-jobs-5276670cf590)

## TO-DO

- SSL
- Autoscaling
- Healthcheck

## Launch in different environments

### (Recommended) dev/stg in container

```
$ docker-compose up [-d]
```

### prod in container

```
docker-compose -f ./docker-compose-prod.yaml up
```

### dev/stg in host os

```
$ CONFIG_PATH="./config-stg.yaml" FLASK_APP=app FLASK_ENV=development flask run
```

### Initialize database

```
$ docker-compose run api-server init-db
$ docker-compose -f ./docker-compose-prod.yaml run --entrypoint flask api-server init-db
```

## Encryption/Decryption Sensitive File with Ansible-Vault

1. Build ansible image

```
$ docker build -t gocreating/ansible-vault -f ansible-vault-dockerfile .
```

2. Encrypt/Decrypt

```
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault encrypt ./configMap-prod.yaml
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault encrypt ./configMap-stg.yaml
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault decrypt ./configMap-prod.yaml
$ docker run -it --rm -v c:/projects/cubee/cubee-api-server/helm-chart/cubee-api-server:/ansible gocreating/ansible-vault decrypt ./configMap-stg.yaml
```

## Touble Shooting

### Docker Compose Error

```
$ docker-compose up
ERROR: readlink /var/lib/docker/overlay2: invalid argument
```

Solution

```
$ docker-compose build --no-cache
```

### Docker Compose Port Forwarding Not Work

Make sure the flask app binds host `0.0.0.0`, ex:

```
$ flask run --host=0.0.0.0
```
