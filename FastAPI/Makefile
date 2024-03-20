build:
	docker compose build

start:
	docker compose up -d

start-build:
	docker compose up --build -d

restart: stop start

rebuild: stop build start

stop:
	docker compose down

clean: db-clean
	docker rmi fastapi-app

db-clean:
	sudo rm -rf ./db/data/
