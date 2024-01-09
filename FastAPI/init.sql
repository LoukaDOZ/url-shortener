CREATE DATABASE url_shortener;
\c url_shortener;

CREATE TABLE url(
    url_id varchar(16) PRIMARY KEY NOT NULL,
    target_url varchar(256) NOT NULL
);