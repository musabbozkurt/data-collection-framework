FROM php:8.3-apache
WORKDIR /var/www/html
# Run Apache unprivileged: listen on 8080 and own the runtime directories as www-data
RUN docker-php-ext-install pdo_mysql sockets opcache \
    && mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" \
    && sed -ri 's/Listen 80$/Listen 8080/' /etc/apache2/ports.conf \
    && sed -ri 's/<VirtualHost \*:80>/<VirtualHost *:8080>/' /etc/apache2/sites-available/*.conf \
    && chown -R www-data:www-data /var/run/apache2 /var/lock/apache2 /var/log/apache2
USER www-data
EXPOSE 8080
