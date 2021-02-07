USE {{ wordpress_database }};
UPDATE {{ table_prefix }}options SET option_value = 'http://{{ domain }}' WHERE option_name = 'siteurl';
UPDATE {{ table_prefix }}options SET option_value = 'http://{{ domain }}' WHERE option_name = 'home';
