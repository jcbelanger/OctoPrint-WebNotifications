#!/usr/bin/env bash

KEYFILE=${OCTOPI_KEYFILE:-/etc/ssl/private/ssl-cert-snakeoil.key}
PEMFILE=${OCTOPI_PEMFILE:-/etc/ssl/certs/ssl-cert-snakeoi.pem}
CERTFILE=${OCTOPI_CERTFILE:-/etc/ssl/snakeoil.pem}
OPENSSLCONF=${OCTOPI_OPENSSLCONF:-/home/pi/octopi_openssl.cnf}
ORIGIN=${ORIGIN:-192.168.1.126}

EXPIRES_TODAY="openssl x509 -checkend 86400 -noout -in ${CERTFILE}"
if true; then # [ ! -f $CERTFILE ] || [ "$(eval $EXPIRES_TODAY)" = "1" ]; then
	touch $KEYFILE
	touch $PEMFILE
	touch $CERTFILE

	openssl req \
		-new \
		-nodes \
		-x509 \
		-days 3650 \
		-keyout $KEYFILE \
		-out $PEMFILE \
		-extensions req_ext \
		-config <( cat $OPENSSLCONF )

	cat $PEMFILE $KEYFILE > $CERTFILE
fi
