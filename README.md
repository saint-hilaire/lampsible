# Lampsible

## About

Complete LAMP stack setup, with a single CLI command. Powered by Ansible under the hood.
This tool can automate almost anything that you'd expect from a LAMP stack.

### Features

* Out of the box LAMP stack
* Custom Apache configuration (custom webroot, vhosts, etc.)
* Apache or MySQL by itself
* WordPress
* Joomla
* Drupal
* Custom Laravel app
* Production ready SSL via Certbot
* SSL for test servers (to avoid being rate limited by Let's Encrypt)
* Self signed SSL, good for local test networks
* Custom PHP version, PHP extensions, Composer packages, etc.
* And so on...


## Requirements

Depends on the use case. The original use case was "via SSH", like most Ansible situations.
This means you have a remote server (or 2 of them, if web and database servers
run on different hosts), where you want to deploy your website. This must be reachable via SSH.
Lampsible will be installed on your local machine.
<br>
However, since v2.1, you can run Lampsible "locally", which means you install Lampsible on the same machine that
will host your website.

### Via SSH

This is the preferred way to use Lampsible.

* Local: Unix system with Python 3.11 or newer. Tested on Ubuntu and Gentoo Linux.
  Might work on macOS, but I haven't tested that. Won't work on Windows,
  because Ansible requires a Unix like system.
* Remote: Ubuntu 20 or newer. You need SSH access and root privilege, or ability to elevate privilege to root.
  Might work on older versions, but I doubt it. Support for other distros is planned in a future version.

### Alternative: running locally

Your machine should be similar to the "Remote" outlined above, Ubuntu Linux. Also, you need root access on that machine.
Ideally, you'll run as a nonprivileged user, and be asked for the root password. Finally, if you run this way, this
should not be some kind production server, but some local test server in a private network.

## Installing

Install with Pip: `python3 -m pip install lampsible`

Or from source:
```
git clone https://github.com/saint-hilaire/lampsible
cd lampsible
python3 -m pip install .
```

## Usage

There are 2 ways to use Lampsible: as a CLI tool, or as a Python library.

### CLI tool

Once you've installed Lampsible onto your local environment, you can run the `lampsible` command.

It takes the format: `lampsible user@host ACTION [OPTIONS]`

If you are running locally, you can simply do: `lampsible localhost ACTION [OPTIONS]`

It is designed to be very simple to use. If you omit some important parameter,
like admin user, password, site title, etc, you will be prompted to enter a value,
or fall back to a default.

Below are some examples:

* Install a production ready WordPress site:

```
lampsible someuser@somehost.com wordpress \
    --email-for-ssl you@yourdomain.com
```

Install a production ready Joomla site:

```
lampsible someuser@somehost.com joomla \
    --email-for-ssl you@yourdomain.com
```

Install Drupal on a test server. Certbot will set up a
test certificate. Also, Apache and MySQL will run on two separate hosts.

```
lampsible someuser@somehost.com drupal \
    --database-system-user-host otheruser@dbserver.somehost.com \
    --database-host 10.0.1.2 \
    --database-username dbuser
    --ssl-test-cert \
    --apache-server-admin you@yourdomain.com \
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

### Python library

Lampsible can be used as a Python library, so if you want to build your own tool,
and want to leverage Lampsible's features to automate various Apache webserver setups,
you can do that.

It could look something like this:

```python
# my_automation_tool.py

from lampsible.lampsible import Lampsible

# Simple WordPress setup
lampsible = Lampsible(
    web_user='someuser',
    web_host='somehost.example.com',
    action='wordpress',
    # Required for Certbot. You can also use email_for_ssl
    apache_server_admin='someuser@example.com',
    database_name='wordpress',
    database_username='db-user',
    database_password='topsecret',
    admin_username='your-wordpress-admin',
    admin_email='wp-admin@example.com',
    admin_password='anothertopsecret',
    site_title='My WordPress Blog',
    # Set this to give your consent to install some required
    # Ansible Galaxy Collections. Otherwise, if any of them are missing,
    # Lampsible will throw an error. If those collections are already installed,
    # this attribute is no longer required.
    # See /src/lampsible/project/ansible-galaxy-requirements.yml
    ansible_galaxy_ok=True,
)

result = lampsible.run()


# Joomla setup. This example is a little more complex,
# to showcase some more features. Webserver and
# database server are two different hosts,
# Certbot will run with the --test-cert flag,
# an older version of Joomla will be installed,
# some custom PHP extensions will be installed
# alongside the ones required by Joomla,
# and some extra environment variables will be set.
lampsible = Lampsible(
    web_user='someuser',
    web_host='somehost.example.com',
    # This assumes that you want your database server
    # to be reachable from the outside via the
    # domain dbserver.example.com, and within your
    # internal network, including your Joomla webserver,
    # via the private IP address 10.0.1.2.
    database_system_user='root',
    database_system_host='dbserver.example.com',
    database_host='10.0.1.2',
    action='joomla',
    email_for_ssl='someuser@example.com',
    ssl_test_cert=True,
    database_name='joomla',
    database_username='db-user',
    database_password='topsecret',
    admin_username='your-joomla-admin',
    admin_email='joomla-admin@example.com',
    admin_password='anothertopsecret',
    # These extensions will be appended to the list of
    # extensions required by the system you are
    # installing (in this case Joomla).
    php_extensions=['php-curl', 'php-gd'],
    joomla_admin_full_name='Your Name',
    joomla_version='5.1.4',
    site_title='My Joomla Site',
    extra_env_vars={'FOO': 'bar', 'HELLO': 'world'}
)

result = lampsible.run()

```

## FAQ

* Why not just use Docker?

Lampsible is intended to be an homage to the old school: A simple and versatile LAMP stack.
If you want something similar with Docker, consider using [Docksible](https://github.com/saint-hilaire/docksible),
another project that I maintain. It will install a web app onto your remote server with Docker Compose.
It also leverages Ansible locally under the hood.

