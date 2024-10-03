FROM mysql:9.0.1
ADD ./db_scripts/testdb.sql /docker-entrypoint-initdb.d/testdb.sql

FROM php:8.0-apache
WORKDIR /var/www/html
RUN apt-get update && apt-get install -y libmariadb-dev
RUN docker-php-ext-install mysqli