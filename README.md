# mptcp-check
A website to check the validity of a mptcp connection

The website is build as a Flask app behind a lighttpd server.
Everything is package in a docker container.

## installing
The first step is to create a directory that will be used for shared files.
``` bash
mkdir /var/docker/mptcp-check
cd /var/docker/mptcp-check
```

The second is to create or download the `lighttpd.conf` file.
``` bash
curl "https://raw.githubusercontent.com/multipath-tcp/mptcp-check/main/lighttpd.conf" > lighttpd.conf
```

You will then need to create the two following scripts. I would recommend the following. Do not forget to set `email` and `url`.

`start.sh`:
``` bash
#!/bin/bash
email= #the email used by certbot
url= #your domain name
path=/var/docker/mptcp-check

sed -i "s#YOUR_URL#${url}#g" ${path}/lighttpd.conf

docker run --rm --name certbot-init \
            -v "${path}/cert:/etc/letsencrypt:rw" \
            -p 80:80 \
            certbot/certbot certonly \
                --non-interactive --agree-tos \
                --email ${email} \
                -d ${url} \
                --standalone

docker run --name mptcp-check \
            -v "${path}/www:/var/www/:ro" \
            -v "${path}/cert/:/etc/letsencrypt/:ro" \
            -v "${path}/lighttpd.conf:/lighttpd.conf:ro" \
            -p 80:80 -p 443:443 \
            --restart unless-stopped \
            --network host \
            --detach \
            mptcp/mptcp-check:main
```

------------------------------------
`renew.sh`
``` bash
#!/bin/bash
email= #the email used by certbot
url= #your domain name
path=/var/docker/mptcp-check
cert="${path}/cert/live/${url}/fullchain.pem"

cert_before=$(sha256sum "${cert}")

docker run --name certbot-renew \
    -v "${path}/www:/var/www/:rw" \
    -v "${path}/cert/:/etc/letsencrypt/:rw" \
    --rm \
    certbot/certbot \
    certonly --non-interactive --agree-tos --webroot \
            --webroot-path /var/www/ \
            --email ${email} \
            -d ${url}

cert_after=$(sha256sum "${cert}")

if [ "${cert_before}" != "${cert_after}" ]; then
    docker restart mptcp-check
fi
```
When the second one has been created, is needs to be added to the crontab and
run frequently.

To create the crontab:
```
crontab -e
```
write `23 2 * * * root /path/to/renew.sh` on a new line

## static files
The server will serve all files and folders in the `/var/www/files` directory.
You can use the following command to create dummy random files of various sizes.
```bash
mkdir -p /var/docker/mptcp-check/www/files && cd $_
for i in 1M 10M 100M 1000M; do
    head -c "${i}" /dev/urandom > "${i}"
done
```

## updating
run the following commands
```
docker pull mptcp/mptcp-check:main

docker stop mptcp-check
docker rm mptcp-check
```
then run the `start.sh` script again.

## update needs
Currently, the apt version of lighttpd is 1.4.63. When the 1.4.76 or newer version is available, `mptcpize run` can be removed from the `Dockerfile` file, and the option `"server.network-mptcp"` can be set in the config.
