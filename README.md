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
* `--ssl-selfsigned`

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
    --ssl-certbot \
    --email-for-ssl you@yourdomain.com
```
(Along with the underlying LAMP stack, this installs WordPress on your server,
and also sets up SSL via Certbot. You don't have to provide any database
or Apache configurations - they will either be generated automatically,
or you will be prompted to enter them.)


**WARNING!** Never set up a WordPress site without immediately navigating to that site
in your browser and finishing the "famous 5 minute WordPress installation",
in which you enter the credentials for the admin user!
Otherwise, someone else will do that for you, and use your server to host malicious content!

## Contributing 

This tool is very much still in beta stage. If you want to help me improve this,
I'll be very happy, just shoot me a message :-)


