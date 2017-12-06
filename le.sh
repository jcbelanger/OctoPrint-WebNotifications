#!/usr/bin/env bash

set -e

if [ $# -ne 1 ]; then
	echo $0: usage: le domain
	exit 1
fi

DOMAIN=$1

echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list.d/raspi.list
apt-get update
apt-get install \
	--no-install-recommends \
	--assume-yes \
	--force-yes \
	--target-release jessie-backports \
	certbot

service haproxy stop

certbot certonly \
	--standalone \
	--agree-tos \
	--non-interactive \
	--register-unsafely-without-email \
	--domain $DOMAIN \
	--domain www.$DOMAIN \
	--preferred-challenges http \
	--http-01-port 80

cd /etc/letsencrypt/live/$DOMIN
cat fullchain.pem privkey.pem > /etc/ssl/snakeoil.pem

service haproxy start
