# Lampsible

## About

Lampsible - LAMP stacks with Ansible and a super simple CLI. This tool can automate anything from
a production ready WordPress site on your VPS to a custom Apache setup on a virtual machine
in your local network.
.

## Requirements

* Local: Unix system with Python 3.8 or newer. Tested on Ubuntu and Gentoo Linux. Might work on macOS, but I haven't tested that. Won't work on Windows.
* Remote: Ubuntu 20 or newer. Might work on older versions, but I doubt it. Support for other distros is planned in a future version.

## Installing

Install with Pip: `python3 -m pip install lampsible`

Alternatively, install from wheel file...: `python3 -m pip install /path/to/local/lampsible-SOME_VERSION-py3-none-any.whl`

... or from source:
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

Install a production ready Joomla site:

```
lampsible someuser@somehost.com joomla \
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

Set up a LAMP stack with various custom configuration and a self signed SSL certificate on some local VM:

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

## Note about PHP versions

Different versions of Ubuntu natively support different versions of PHP.
You can specify the PHP version to install on the remote server by
passing the `--php-version` flag. The default value for this parameter is
currently: **8.3**

If you try to install an unsupported PHP version on your remote server,
Lampsible will fail, because on the remote server, APT will fail to find
the required packages. Therefore, you need to pass the correct value to
the `--php-version` flag. Based on your Ubuntu version, these currently are:

* Ubuntu 24: PHP 8.3 (default)
* Ubuntu 23: PHP 8.2 (not tested)
* Ubuntu 22: PHP 8.1
* Ubuntu 20: PHP 7.4

A future version of Lampsible will improve this. The default will be the
newest version of PHP, but if Lampsible detects that you are trying to
install an unsupported PHP version on your remote Ubuntu server, Lampsible
will warn you, and offer to overwrite the value with a value that's supported.
That way, you won't have to worry about PHP versions altogether.

However, for now, you do have to be mindful of the Ubuntu version, and specify
the correct PHP version.

Of course, you can also add support for other PHP versions on your remote
server by manually configuring the APT repository.

It's also worth noting that Joomla 5 requires PHP 8.1 or newer. Similar
requirements may apply for other CMS/frameworks like Wordpress, Laravel, etc.

## Contributing 

Please do! I'd be more than happy to see Issues, Pull Requests and any other kind of feedback ;-)
