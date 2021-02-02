CREATE USER '{{mysql_user}}'@'localhost' IDENTIFIED BY '{{mysql_password}}';
GRANT ALL PRIVILEGES ON * . * TO '{{mysql_user}}'@'localhost';
FLUSH PRIVILEGES;
