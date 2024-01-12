CREATE DATABASE url_shortener;
\c url_shortener;

CREATE TABLE users(
    username varchar(32) PRIMARY KEY NOT NULL,
    password varchar(64) NOT NULL
);

CREATE TABLE url(
    url_id varchar(8) PRIMARY KEY NOT NULL,
    target_url varchar(512) NOT NULL,
    username varchar(32) REFERENCES users(username)
);