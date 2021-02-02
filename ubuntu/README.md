The gist of this is to set up a Wordpress-site on a LAMP-stack.  
Generally, it should go like this:  
`ansible-playbook lamp-stack.yml --extra-vars "mysql_user=[alice] mysql_password=[ecila]"`  
`ansible-playbook ssl-selfsigned.yml --extra-vars "server_admin=[me@me.com]"`  
`ansible-playbook wordpress.yml --extra-vars "mysql_user=[alice] mysql_password=[ecila]"`  
