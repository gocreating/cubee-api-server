# Cubee API Server

## GKE Setup

### 建立Cluster

開機器時storage預設100G，但下限其實可以降到10G，否則帳單會破表

### Helm權限

[Helm 部署在 GKE 上的權限問題](https://medium.com/smalltowntechblog/helm-tiller-%E9%83%A8%E7%BD%B2%E5%9C%A8-gke-%E4%B8%8A%E7%9A%84%E6%AC%8A%E9%99%90%E5%95%8F%E9%A1%8C-a016f703372e)

由於ci的job裡會去建立k8s的service account，以便後續執行helm指令，但GKE預設的權限是不足的，必須調整才能順利部署。

要將`833974311137-compute@developer.gserviceaccount.com`, `Compute Engine default service account` 新增腳色: `Kubernetes Engine 管理`

### 首次部署

第一次deploy時，circle-ci的job裡去會啟動k8s的tiller，所以可能會因為tiller還沒ready，導致首次deploy失敗

可以打開 cloud console輸入

``` bash
$ kubectl -n kube-system get po
```

看結果有沒有長得像`tiller-deploy-2654728925-j2zvk`的pod name

如果有，可以rerun看看ci的job

### Nginx Ingress Controller

[NGINX Ingress Controller Installation Guide](https://kubernetes.github.io/ingress-nginx/deploy/)

``` bash
# 這個只有在第一個cluster建立時執行一次即可，第二個cluster就不用執行了
$ kubectl create clusterrolebinding cluster-admin-binding \
  --clusterrole cluster-admin \
  --user $(gcloud config get-value account)
Your active configuration is: [cloudshell-24112]
clusterrolebinding.rbac.authorization.k8s.io/cluster-admin-binding created

$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml
namespace/ingress-nginx created
configmap/nginx-configuration created
configmap/tcp-services created
configmap/udp-services created
serviceaccount/nginx-ingress-serviceaccount created
clusterrole.rbac.authorization.k8s.io/nginx-ingress-clusterrole created
role.rbac.authorization.k8s.io/nginx-ingress-role created
rolebinding.rbac.authorization.k8s.io/nginx-ingress-role-nisa-binding created
clusterrolebinding.rbac.authorization.k8s.io/nginx-ingress-clusterrole-nisa-binding created
deployment.apps/nginx-ingress-controller created

$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/cloud-generic.yaml
service/ingress-nginx created
```

檢查是否有安裝正確
``` bash
$ kubectl get service ingress-nginx --namespace=ingress-nginx
NAME            TYPE           CLUSTER-IP   EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx   LoadBalancer   10.28.5.20   <pending>     80:31222/TCP,443:30889/TCP   29s
```

### 將LB的IP改為Static並設定DNS

接著要將ingress的ip從`臨時`改為`靜態`，給定名字後（例如`nginx-ingress-prod`）就可以到域名服務商把domain指向這個靜態IP了

### 關閉不必要的外掛

[降低小型叢集中的外掛程式資源使用量](https://cloud.google.com/kubernetes-engine/docs/how-to/small-cluster-tuning?hl=zh-tw)

``` bash
$ gcloud container clusters update cubee-prod --zone us-west1-a --update-addons=KubernetesDashboard=DISABLED
Updating cubee-prod...done.
Updated [https://container.googleapis.com/v1/projects/cubee-247317/zones/us-west1-a/clusters/cubee-prod].
```

``` bash
$ gcloud container clusters update cubee-prod --zone us-west1-a --logging-service none
Updating cubee-prod...done.
Updated [https://container.googleapis.com/v1/projects/cubee-247317/zones/us-west1-a/clusters/cubee-prod].
To inspect the contents of your cluster, go to: https://console.cloud.google.com/kubernetes/workload_/gcloud/us-west1-a/cubee-prod?project=cubee-247317
```

``` bash
$ kubectl scale --replicas=0 deployment/kube-dns-autoscaler --namespace=kube-system
deployment.extensions/kube-dns-autoscaler scaled
$ kubectl scale --replicas=1 deployment/kube-dns --namespace=kube-system
deployment.extensions/kube-dns scaled
```

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

### 您的叢集有一或多個無法排程的 pod

[調整叢集大小](https://cloud.google.com/kubernetes-engine/docs/how-to/resizing-a-cluster?hl=zh-tw)

``` bash
# gcloud container clusters resize [CLUSTER_NAME] --node-pool [POOL_NAME] --size [SIZE]
$ gcloud container clusters resize cubee-prod --node-pool default-pool --size 4 --zone us-west1-a
Pool [default-pool] for [cubee-prod] will be resized to 4.

Do you want to continue (Y/n)?  y

Resizing cubee-prod...done.
Updated [https://container.googleapis.com/v1/projects/cubee-247317/zones/us-west1-a/clusters/cubee-prod].
```

### 如何在 Circle CI 的 Job 間共享檔案

起因主要是要將解密過的config餵給helm/k8s，但是解密和部署分別跑在不同的image和job，所以必須要想辦法共享解密過的檔案，[官方文件](https://circleci.com/docs/2.0/workflows/#using-workspaces-to-share-data-among-jobs)實在寫得太爛了，找了好久才找到以下文章解套

- [CircleCI: Persisting Environment Variables Across Steps and Jobs](https://medium.com/@johnthughes/circleci-persisting-environment-variables-across-steps-and-jobs-5276670cf590)
