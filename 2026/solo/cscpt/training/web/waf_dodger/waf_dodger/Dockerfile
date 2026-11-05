FROM php:7.4-apache

COPY src /var/www/html

ARG flag

RUN echo $flag > /var/www/html/secrets/flag.txt
