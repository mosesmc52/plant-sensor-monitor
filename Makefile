COMPOSE = docker compose -f server/docker/docker-compose.yml

.PHONY: build up up-d down

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up

up-d:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down
