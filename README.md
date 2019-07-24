# Cubee API Server

## GKE Setup

[Helm 部署在 GKE 上的權限問題](https://medium.com/smalltowntechblog/helm-tiller-%E9%83%A8%E7%BD%B2%E5%9C%A8-gke-%E4%B8%8A%E7%9A%84%E6%AC%8A%E9%99%90%E5%95%8F%E9%A1%8C-a016f703372e)

要將`833974311137-compute@developer.gserviceaccount.com`, `Compute Engine default service account` 新增腳色: `Kubernetes Engine 管理`

要將ingress的ip從`臨時`改為`靜態`，給定名字後修改`ingress.yaml`裡的`kubernetes.io/ingress.global-static-ip-name`

## Development

```
$ FLASK_ENV=development python app/app.py
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
