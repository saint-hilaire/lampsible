/*
TODO: feature/fix-mysql
 */
USE {{ database_name }};
UPDATE {{ database_table_prefix }}options SET option_value = 'http://{{ domain_for_wordpress }}' WHERE option_name = 'siteurl';
UPDATE {{ database_table_prefix }}options SET option_value = 'http://{{ domain_for_wordpress }}' WHERE option_name = 'home';
