# OctoPrint-WebNotifications

This plugin provides HTML5 Web Push Notifications for OctoPrint completed jobs.  This allows you to recieve web push notifications where Web Push Notifications are implemented, see [browser support for Push API](https://caniuse.com/#feat=push-api).  Android and most desktop browsers implement this service, while notably iPhone does not yet support it.  However, [progress is being made](https://webkit.org/status/#specification-service-workers) and when completed, this plugin should work there as well.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/jcbelanger/OctoPrint-WebNotifications/archive/master.zip

## Secure Origin

Web browsers will only offer web notifications if your OctoPrint instance is served from a "secure origin"!  Examples of secure origins are `localhost` and websites served through https with valid certificates.  For OctoPi users, this means the default self-signed certificate will not work!  The basic steps for serving your home OctoPi instance from a secure origin are:

1. Create a user for OctoPrint.  It would be irresponsible to expose your OctoPrint instance to the public without any authentication.
2. Configure your home router to forward TCP traffic on ports 80 and 443 to your OctoPrint instance.
3. Register a domain pointing to your home router.  There a number of services that offer free domains.  
4. Use LetsEncrypt to generate a free https certificate for your domain.  I've included `le.sh` for this purpose.  For example if your domain was `mypi.ga`, you would run the script as 
    
    `./le.sh mypi.ga`

## Overview of le.sh

1. The `le.sh` script will install LetsEncrypt's certbot tool. 
2. It will then temporarily stop OctoPi's HAProxy for certbot. 
3. Certbot will request a new certificate for your domain by answering Let's Encrypt's validation challenges.
4. It will then overwrite the existing self-signed cert with the certificate from letsencrypt.  (TODO: It should configure HAProxy).  
5. It will then restart HAProxy to enable the new cert.
6. TODO: I need to create a cron job to automatically renew the certifiacte -- This isn't a problem for most home users as the certificate only needs to be valid once for the browser to allow push notifications.


## Gotchas

* You may need to clear your cache before your browser begins to recognize the new certificate.
* You may need to re-enable push notifications for the site if you accidientally disallow the site's permission request.
