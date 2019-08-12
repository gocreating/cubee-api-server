# Setup Wildcard TLS

## 重新取得憑證

如果是首次取得憑證，請忽略此步驟
如果非首次取得憑證，請先清理先前產生的金鑰檔及k8s secret

> 移除secret可能會造成down time，如果有疑慮，可以使用 kubectl apply 或 kubectl replace 避免 down time

``` bash
$ sudo rm -rf certbot/*
$ rm ./fullchain.pem ./privkey.pem
$ kubectl delete secret cubee-cc-tls
```

## 取得憑證

``` bash
# https://certbot-dns-google.readthedocs.io/en/stable/
$ mkdir certbot
$ docker run -it --rm -v /home/gocreating/certbot:/etc/letsencrypt -v /home/gocreating:/tmp certbot/dns-google:v0.36.0 \
    certonly \
    --dns-google \
    --dns-google-credentials "/tmp/cubee-247317-a6d942d9d037(certbot).json" \
    --email gocreating@gmail.com \
    -d cubee.cc \
    -d "*.cubee.cc" \
    -d "*.stg.cubee.cc" \
    --agree-tos \
    --non-interactive \
    --dns-google-propagation-seconds 80

    # --cert-path /etc/xxx.pem \
    # --key-path /etc/xxx.pem \
    # --fullchain-path /etc/xxx.pem \
    # --chain-path /etc/xxx.pem \
    # --dry-run
$ sudo cp certbot/live/cubee.cc/fullchain.pem .
$ sudo cp certbot/live/cubee.cc/privkey.pem .
$ sudo chmod 777 fullchain.pem
$ sudo chmod 777 privkey.pem
$ kubectl create secret tls cubee-cc-tls --cert fullchain.pem --key privkey.pem
secret/cubee-cc-tls created
```

## 更新憑證

``` bash
$ docker run -it --rm -v /home/gocreating/certbot:/etc/letsencrypt -v /home/gocreating:/tmp  certbot/dns-google:v0.36.0 \
    renew \
    --cert-name cubee.cc \
    --dns-google-propagation-seconds 80
    # --force-renewal
Saving debug log to /var/log/letsencrypt/letsencrypt.log

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/cubee.cc.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Plugins selected: Authenticator dns-google, Installer None
Renewing an existing certificate

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
new certificate deployed without reload, fullchain is
/etc/letsencrypt/live/cubee.cc/fullchain.pem
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

Congratulations, all renewals succeeded. The following certs have been renewed:
  /etc/letsencrypt/live/cubee.cc/fullchain.pem (success)
```

更新k8s設定

``` bash
$ sudo cp certbot/live/cubee.cc/fullchain.pem .
$ sudo cp certbot/live/cubee.cc/privkey.pem .
$ sudo chmod 777 fullchain.pem
$ sudo chmod 777 privkey.pem
$ kubectl delete secret cubee-cc-tls
$ kubectl create secret tls cubee-cc-tls --cert fullchain.pem --key privkey.pem
```
