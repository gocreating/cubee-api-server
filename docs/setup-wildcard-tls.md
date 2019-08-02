godaddy預設的cubee.cc的nameserver

ns19.domaincontrol.com
ns20.domaincontrol.com

<!-- https://certbot-dns-google.readthedocs.io/en/stable/ -->
```
$ mkdir certbot
$ docker run -it --rm -v /home/gocreating/certbot:/etc/letsencrypt -v /home/gocreating:/tmp certbot/dns-google:v0.36.0 \
    certonly \
    --dns-google \
    --dns-google-credentials "/tmp/cubee-247317-a6d942d9d037(certbot).json" \
    --email gocreating@gmail.com \
    -d cubee.cc \
    -d "*.cubee.cc" \
    --agree-tos \
    --non-interactive \
    --dns-google-propagation-seconds 80

    # --cert-path /etc/xxx.pem \
    # --key-path /etc/xxx.pem \
    # --fullchain-path /etc/xxx.pem \
    # --chain-path /etc/xxx.pem \
    # --dry-run
$ sudo cp certbot/live/cubee.cc/cert.pem .
$ sudo cp certbot/live/cubee.cc/privkey.pem .
$ sudo chmod 777 cert.pem
$ sudo chmod 777 privkey.pem
$ kubectl create secret tls cubee-cc-tls --cert cert.pem --key privkey.pem
secret/cubee-cc-tls created
```
