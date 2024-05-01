# Lampsible

## About

Lampsible - LAMP stacks with Ansible and a super simple CLI. This tool can automate anything from
a production ready WordPress site on your VPS to a custom Apache setup on a virtual machine
in your local network.
.

## Installing

Install with Pip: `python3 -m pip install lampsible`

Alternatively, install from source:
```
git clone https://github.com/saint-hilaire/lampsible
cd lampsible
python3 -m pip install .
```


## Sample usage

Lampsible is designed to be very simple to use. If you forget some important
parameter, Lampsible will prompt you for it, or pick some sensible defaults.


Install Apache on your server:

```
lampsible someuser@somehost.com apache
```

Install a production ready WordPress site:

```
lampsible someuser@somehost.com wordpress \
    --ssl-certbot \
    --email-for-ssl you@yourdomain.com
```

Install a Laravel app on a test server:

```
lampsible someuser@somehost.com laravel \
    --ssl-certbot \
    --test-cert \
    --apache-server-admin you@yourdomain.com \
    --app-name cool-laravel-app \
    --app-build-path /path/to/your/local/cool-laravel-app-0.7rc.tar.gz \
    --laravel-artisan-commands key:generate,migrate
```

Set up a LAMP with various custom configuration and a self signed SSL certificate on some local VM:

```
lampsible someuser@192.168.123.123 lamp-stack \
    --ask-remote-sudo \
    --ssl-selfsigned \
    --database-username dbuser \
    --database-name testdb \
    --php-version 8.1 \
    --apache-vhost-name some-legacy-app \
    --apache-document-root /var/www/html/some-legacy-app/some-dir/public \
    --php-extensions mysql,xml,mbstring,xdebug,gd
```


Run `lampsible --help` for a full list of options.

## Contributing 

PLease do! I'd be more than happy to see Issues, Pull Requests and any other kind of feedback ;-)
