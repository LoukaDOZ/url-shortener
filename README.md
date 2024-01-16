# URL Shortener

URL Shortener is a little web app that, from a given URL, associates an smaller and more convenient one.
The goal of this project is to make a first step in web app developement using Python.

3 versions of this project exist, one for each of the following web framework:
- [FastAPI](FastAPI/)
- [Flask](Flask/)
- [Django](Django/)

### Usage

Each project can be easy launch through a `Makefile` and a `docker-compose.yml`.

| Command            | Description                                                     |
| ------------------ | --------------------------------------------------------------- |
| `make build`       | Build Docker containers                                         |
| `make start`       | Start Docker containers                                         |
| `make start-build` | Rebuild Dockerfiles and start Docker containers                 |
| `make restart`     | Restart Docker containers                                       |
| `make rebuild`     | Rebuild Dockerfiles and restart Docker containers               |
| `make stop`        | Stop Docker containers                                          |
| `make db-clean`    | Delete database volume and remove all data (require to be root) |

Project is then locally accessible via : http://localhost:8080.

## Features

All projects will share the same features. Some tools and libraries may differ, but it will always be a Python web app and a database.

### URL shortening

Shortening an URL gives a smaller one. When used, this shortened URL redirects to the original one.

### Account

All projects include a way to register and login. Shortening URLs when logged allows the user to retrieve all the URL he has shortened in a dedicated page.

When the user tries to shorten an URL without beeing connected, a log in page is shown before the shortening. He can continue as a guest if he doesn't want to log in or register a new account.

### Expiration date

A shortened URL have an expiration date of 7 days after its creation. Once it expires, it is not usable anymore and will lead to a not found error.

Expired URLs are automatically removed from the database every time a shortened URL is used. It prevents populating it with useless data. This solution was the simpliest to implement but is surely not perfect.