#!/usr/bin/env bash

set -e -o pipefail


if [ $# -ne 1 ]; then
	echo $0: "usage: le domain"
	exit 1
fi
DOMAIN=$1


if ! [ -x "$(command -v certbot)" ]; then
	SOURCES="/etc/apt/sources.list.d/raspi.list"
	
	#Raspbian fix.  See https://github.com/certbot/certbot/issues/2673 for details
	RASPBIAN_TESTING="deb http://mirrordirector.raspbian.org/raspbian/ testing main contrib non-free rpi"
	if ! grep --quiet "^$RASPBIAN_TESTING" /etc/apt/sources.list /etc/apt/sources.list.d/*.list; then
		echo "Applying fix for raspbian certbot install"
		echo "$RASPBIAN_TESTING" >> /etc/apt/sources.list
	fi

	echo "Installing certbot..."
	apt-get update
	apt-get install \
		--no-install-recommends \
		--assume-yes \
		--force-yes \
		certbot
	echo "Installed certbot!"
fi


#We stop haproxy to run the certbot as a acme server on port 80
#TODO update haproxy config to forward acme requests to certbot so we can avoid downtime
echo "Stopping haproxy..."
service haproxy stop
echo "haproxy stopped!"


echo "Registering $DOMAIN with letsencrypt..."
certbot certonly \
	--standalone \
	--agree-tos \
	--non-interactive \
	--register-unsafely-without-email \
	--domain $DOMAIN \
	--domain www.$DOMAIN \
	--preferred-challenges http \
	--http-01-port 80
echo "Registered $DOMAIN with letsencrypt!"


#TODO modify haproxy config instead of overwriting the included octopi self signed cert
SELF_SIGNED_CERT="/etc/ssl/snakeoil.pem"
LETS_ENCRYPT_CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
LETS_ENCRYPT_PRIV_KEY="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
if [ -f $LETS_ENCRYPT_CERT ] && [ -f $LETS_ENCRYPT_CERT ]; then
	echo "Overwriting the self-signed cert with one from letsencrypt..."
	rm --force $SELF_SIGNED_CERT
	cat $LETS_ENCRYPT_CERT  $LETS_ENCRYPT_PRIV_KEY > $SELF_SIGNED_CERT
	echo "Overwrote the self-signed cert with one from letsencrypt!"
fi


echo "Starting haproxy..."
service haproxy start
echo "haproxy started!"


#TODO create cronjob to autorenew cert


echo "You should now open your browser to https://$DOMAIN to view the website"
