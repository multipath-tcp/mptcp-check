# mptcp-check
A website to check the validity of a mptcp connection

The website is build as a Flask app behind a lighttpd server.
Everything is package in a docker container.

## installing
you will need to create the too following scripts. I would recommend the following. Do not forget to replace the `email` and `url`

`start.sh`:
``` bash
#!/bin/bash
email= #the email used by certbot
url= #your domain name
path=/var/docker/mptcp-check

docker run --rm --name certbot-init \
            -v "$path/cert:/etc/letsencrypt:rw" \
            -p 80:80 \
            certbot/certbot certonly \
                --non-interactive --agree-tos \
                --email $email \
                -d $url \
                --standalone

docker run --name mptcp-check \
            -v "$path/www:/var/www/:ro" \
            -v "$path/cert/:/etc/letsencrypt/:ro" \
            -p 80:80 -p 443:443 \
            --restart unless-stopped \
            --network host \
            --detach \
            mux514/mptcp-check:main
```

------------------------------------
`renew.sh`
``` bash
#!/bin/bash
email= #the email used by certbot
url= #your domain name
path=/var/docker/mptcp-check

cert-before=$(sha256sum certbot/conf/live/$url/fullchain.pem)

docker run --name certbot-renew \
    -v "$path/www:/var/www/:rw" \
    -v "$path/cert/:/etc/letsencrypt/:rw" \
    --detach \
    certbot/certbot \
    certonly --non-interactive --agree-tos --webroot \
            --webroot-path /var/www/ \
            --email $email \
            -d $url

cert-after=$(sha256sum certbot/conf/live/$url/fullchain.pem)

if [ cert-before != cert-after ] then
    docker restart mptcp-check
fi
```
When the second one has been created, is needs to be added to the crontab and
run frequently.

To create the crontab:
```
crontab -e
```
write `0 0 * * * root /path/to/renew.sh` on a new line

## static files
The server will serve all files and folders in the `/var/www/files` directory.
You can use the following command to create dummy random files of various sizes.
```
mkdir -p /var/docker/mptcp-check/www/files
for i in 1M 10M 100M 1000M; do
    head -c "${i}" /dev/urandom > "/var/docker/mptcp-check/www/files/${i}"
done
```

## updating
run the following commands
```
docker pull mux514/mptcp-check:main

docker stop mptcp-check
docker rm mptcp-check
```
then run the `start.sh` script again.

## update needs
Currently, the apt version of lighttpd is 1.4.63, when the 1.4.76 is available, the last line of the `Dockerfile` should be swapped with the comment above.