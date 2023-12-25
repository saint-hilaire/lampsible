CREATE USER '{{ database_username }}'@'localhost' IDENTIFIED BY '{{ database_password }}';
GRANT ALL PRIVILEGES ON * . * TO '{{ database_username }}'@'localhost';
FLUSH PRIVILEGES;
