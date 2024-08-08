# URL Shortener

URL Shortener is a web app that, from a given URL, associates an smaller and more convenient one.
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
| `make clean`       | Delete database volume and docker images (require root)         |
| `make db-clean`    | Delete database volume (require root)                     |

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

## Screenshots

### Shorten page
![Capture d’écran du 2024-03-13 12-24-44](https://github.com/LoukaDOZ/url-shortener/assets/46566140/ec46b231-8404-4ff4-b80d-02b180c7d14d)

### Shortened URL page
![Capture d’écran du 2024-03-13 12-25-13](https://github.com/LoukaDOZ/url-shortener/assets/46566140/01b7f28d-cc9d-4e2d-bdd0-d62d36a0d8b3)

### My shortened URLs page
![Capture d’écran du 2024-03-13 12-28-00](https://github.com/LoukaDOZ/url-shortener/assets/46566140/9d7287d4-c479-44aa-b3d6-0ff6e6ab55f7)

### Login/Register page
![Capture d’écran du 2024-03-13 12-25-43](https://github.com/LoukaDOZ/url-shortener/assets/46566140/f129722b-7810-4352-89a1-51d873b3660e)

### Login/Register page while shortening
![Capture d’écran du 2024-03-13 12-25-04](https://github.com/LoukaDOZ/url-shortener/assets/46566140/e86cb710-c033-4e3f-ae49-192e9dd6ae9f)
