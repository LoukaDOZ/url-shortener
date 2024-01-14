.PHONY: list

list:
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'

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

db-clean:
	sudo rm -rf ./db/data/