# Cubee API Server

## GKE Setup

[Helm 部署在 GKE 上的權限問題](https://medium.com/smalltowntechblog/helm-tiller-%E9%83%A8%E7%BD%B2%E5%9C%A8-gke-%E4%B8%8A%E7%9A%84%E6%AC%8A%E9%99%90%E5%95%8F%E9%A1%8C-a016f703372e)

要將`833974311137-compute@developer.gserviceaccount.com`, `Compute Engine default service account` 新增腳色: `Kubernetes Engine 管理`

## Development

```
$ FLASK_ENV=development python app/app.py
```
