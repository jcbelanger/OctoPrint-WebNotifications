#!/usr/bin/env bash

set -e


if [ $# -ne 1 ]; then
	echo $0: "usage: le domain"
	exit 1
fi
DOMAIN=$1


if ! [ -x "$(command -v certbot)" ]; then
	echo "Installing certbot from jessie-backports..."
	
	BACK_PORTS="deb http://ftp.debian.org/debian jessie-backports main"
	SOURCES="/etc/apt/sources.list.d/raspi.list"
	if ! grep --quiet "^$BACK_PORTS" $SOURCES /etc/apt/sources.list.d/*; then
		echo "Adding jessie-backports"
		echo "$BACK_PORTS" >> $SOURCES
	fi

	apt-get update
	apt-get install \
		--no-install-recommends \
		--assume-yes \
		--force-yes \
		--target-release jessie-backports \
		certbot
	
	echo "Installed certbot from jessie-backports!"
fi


if false; then
	echo "Registering $DOMAIN with letsencrypt..."
	
	#We stop haproxy to run the certbot as a acme server on port 80
	#TODO update haproxy config to forward acme requests to certbot
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

	service haproxy start
	
	echo "Registered $DOMAIN with letsencrypt!"
fi


#TODO modify haproxy config instead of overwriting the included octopi self signed cert
HAPROXY_CERT="/etc/ssl/snakeoil.pem"
LETS_ENCRYPT_CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
LETS_ENCRYPT_PRIV_KEY="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
if [ -f $LETS_ENCRYPT_CERT] && [ -f $LETS_ENCRYPT_CERT]; then
	echo "Applying letsencrypt cert to haproxy..."
	rm --force $HAPROXY_CERT
	cat $LETS_ENCRYPT_CERT  $LETS_ENCRYPT_PRIV_KEY > $HAPROXY_CERT
	service haproxy reload
fi


#TODO create cronjob to autorenew cert
