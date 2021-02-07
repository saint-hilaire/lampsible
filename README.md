# yap
## Yet Another Playbook

These are Ansible Playbooks that I find useful. Right now, only Ubuntu stuff works, so cd into that directory and run the playbooks.  

These scripts are currently geared toward automatically deploying Wordpress-sites, but you can also use them to deploy LAMP-stacks, and do SSL-stuff independently of Wordpress.  

The following playbooks require following `--extra-vars` to be set:  
`lamp-stack.yml`: `mysql_user` and `mysql_password`  
`ssl-selfsigned.yml`:  `server_admin` (an email-address, can be fake, like me@me.com\)    
`wordpress.yml`: `mysql_user` and `mysql_password`  
`domain-letsencrypt.yml`: `domain` and `admin_email`  
`domain-wordpress.yml`: `domain`  


### General workflow:  
Set up a LAMP-stack.  
`ansible-playbook lamp-stack.yml --extra-vars "mysql_user=alice mysql_password=ecila"`  

Set up a self-signed SSL-certificate for your testing-environment.  
`ansible-playbook ssl-selfsigned.yml --extra-vars "server_admin=me@me.com"`  

Install Wordpress.  
`ansible-playbook wordpress.yml --extra-vars "mysql_user=alice mysql_password=ecila"`  

Now at some point later on, take your test-environment live into production.  
First, get an SSL-Certificate from Let's Encrypt:  
`ansible-playbook domain-letsencrypt.yml --extra-vars "domain=example.com admin_email=admin@example.com"`  

Now, configure Wordpress to use your domain. This requires that you had finalised setting up Wordpress in your browser, i.e. you gave it a site-tite, user-name and password:  
`ansible-playbook domain-wordpress.yml --extra-vars "domain=example.com"`  

### Alternative workflow, if you want to skip the testing-environment-self-signed-stuff and go straight to production with a real domain:  
Set up a LAMP-stack.  
`ansible-playbook lamp-stack.yml --extra-vars "mysql_user=[alice] mysql_password=[ecila]"`  

Install Wordpress.  
`ansible-playbook wordpress.yml --extra-vars "mysql_user=[alice] mysql_password=[ecila]"`  

Get an SSL-Certificate from Let's Encrypt:  
`ansible-playbook domain-letsencrypt.yml --extra-vars "domain=example.com admin_email=admin@example.com"`  

Now, configure Wordpress to use your domain. This requires that you had finalised setting up Wordpress in your browser, i.e. you gave it a site-tite, user-name and password:  
`ansible-playbook domain-wordpress.yml --extra-vars "domain=example.com"`  

### Notes   
If you don't want to run Wordpress on your server, i.e. just a just a LAMP-stack, with or without SSL (Let's Encrypt or self-signed), then simply run only those playbooks that you require, and exclude the playbooks `wordpress.yml` and `domain-wordpress.yml` from your workflow.  
If you want to get test-certificates from Let's Encrypt's staging server, instead of live-certificates, edit `roles/domain-letsencrypt/tasks/main.yaml`, uncomment the line `raw: "certbot --test-cert blabla"`, and comment out the line below it, that doesn't contain the `--test-cert`-flag.
