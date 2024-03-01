# Lampsible

## About

Lampsible - LAMP stacks with Ansible and a super simple CLI. You can use this tool to set up a
LAMP stack with Ansible. That is, on a given Linux server, install Apache, MySQL, PHP,
and some web application of your choice. Under the hood, it utilizes Ansible, a
powerful server automation tool, but you don't have to worry about writing
Ansible Playbooks or configuring inventories and hosts, because Lampsible
does all of that for you. You just use the CLI to tell Lampsible where your server is,
what you want to install on it, and Lampsible does everything for you.

## Installing

Install with Pip: `python3 -m pip install lampsible`

Alternatively, install from source:
```
git clone https://github.com/saint-hilaire/lampsible
cd lampsible
python3 -m pip install .
```

You can also run the Python code directly, but this option is geared more towards
developers (also, it's not really necessary, because you can install from source
and pass the `--editable` flag): `python3 src/lampsible/lampsible.py --help`


## Usage

General usage looks like this:

```
lampsible REMOTE_USER REMOTE_HOST DESIRED_ACTION [OPTIONAL_FLAGS]
```

Currently supported actions are:

* `lamp-stack`
* `apache`
* `mysql`
* `php`
* `wordpress`
* `dump-ansible-facts`

Some flags which you'll likely also want to use:

* `--apache-vhost-name`
* `--database-username`
* `--php-version` (You'll need this on older Ubuntu versions, because they don't support PHP 8 out of the box)
* `--wordpress-version`
* `--ssl-certbot`
* `--ssl-selfsigned` (See the note below about Certbot)

Run `lampsible --help` for a full list of options.

### Sample usage

```
lampsible sampleuser your.server.com lamp-stack \
    --apache-vhost-name    my-site \
    --apache-document-root /var/www/html/my-site/public \
    --database-username    dbuser \
    --database-name        my_database
```
(This installs Apache, MySQL and PHP. Because a database user and name are provided,
they are created as well - otherwise they won't be created. You don't need to enter a database
password, as it's generally insecure to do so over the CLI. Lampsible will prompt you for a password.)

<br>

```
lampsible sampleuser your.server.com wordpress \
    --ssl-selfsigned
```
(Along with the underlying LAMP stack, this installs WordPress on your server,
and also sets up a self signed SSL certificate, so you have a secure connection
to finish setting up your WordPress site. You don't have to provide any database
or Apache configurations - they will either be generated automatically,
or you will be prompted to enter them.)


**WARNING!** Never set up a WordPress site without immediately navigating to that site
in your browser and finishing the "famous 5 minute WordPress installation",
in which you enter the credentials for the admin user!
Otherwise, someone else will do that for you, and use your server to host malicious content!

### Note about Certbot

Certbot is not completely working at the moment. It works, but you have to do
part of the process directly on the remote server. There is also a little bit
of difficutly with WordPress at the moment, because immediately after Lampsible
finishes installing WordPress, (but before you finish the _"famous 5-minute install"_
in the browser), the tables of the WP database won't exist yet, but in order for Certbot to
work, they need to exist.

For this reason, to install a fully functional, secure, production ready WordPress site,
the workflow will need to look something like this:

* First, install WordPress with the along with an self signed SSL certificate, so you have an
  encrypted connection over which you can securely provide your admin credentials.
```
lampsible remoteuser your.server.com wordpress --ssl-selfsigned --apache-server-admin you@yourdomain.com
```

* Next, finish setting up WordPress by browsing to your new site and completing
  the _"famous 5 minute install"_ - it takes a lot less than 5 minutes, but it
  is **very important** that you do this immediately, because otherwise someone could
  hijack your site by doing this step for you.

* Now, rerun the lampsible command from before, but with the
  `--ssl-certbot` flag instead of `--ssl-selfsigned`.
```
lampsible remoteuser your.server.com wordpress --ssl-certbot --apache-server-admin you@yourdomain.com
```

* Finally, SSH into your remote server, then, as root, run `certbot`.
  Note that for WordPress sites, you'll have to enable SSL
  not just for your.server.com but also www.your.server.com.
  When Certbot prompts you to select a virtual host for which to to enable SSL,
  select `wordpress-ssl.conf`. (That is assuming that you did not provide
  an `--apache-vhost-name` of your own - in any case, pick the one with the `-ssl` in its name).


## Contributing 

This tool is very much still in beta stage. If you want to help me improve this,
I'll be very happy, just shoot me a message :-)


