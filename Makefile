.PHONY: help install-dev run-dev run-dev-d display-dev test-dev \
	docker-dev docker-dev-down docker-dev-display \
	install-pi run-pi run-pi-d display-pi docker-pi docker-pi-down docker-pi-display \
	build up up-d down

DOCKER_COMPOSE ?= docker compose
DEV_COMPOSE = $(DOCKER_COMPOSE) -f server/docker/docker-compose.dev.yml
PI_COMPOSE = $(DOCKER_COMPOSE) -f server/docker/docker-compose.pi.yml

help:
	@printf '%s\n' \
		'Development:' \
		'  make install-dev         Install Python dependencies in Docker' \
		'  make run-dev             Run the FastAPI server in Docker' \
		'  make run-dev-d           Run the FastAPI server in Docker as a daemon' \
		'  make display-dev         Render a development display preview in Docker' \
		'  make test-dev            Compile-check the server code in Docker' \
		'  make docker-dev          Build and run the development Docker service' \
		'  make docker-dev-down     Stop the development Docker service' \
		'' \
		'Raspberry Pi:' \
		'  make install-pi          Install dependencies in the Pi container' \
		'  make run-pi              Run the FastAPI server in Docker on the Pi' \
		'  make run-pi-d            Run the FastAPI server in Docker on the Pi as a daemon' \
		'  make display-pi           Update the physical Waveshare display in Docker' \
		'  make docker-pi           Build and run the Pi Docker service' \
		'  make docker-pi-down      Stop the Pi Docker service' \
		'  make docker-pi-display   Update the display from the Pi container'

install-dev:
	$(DEV_COMPOSE) run --build --rm plant-monitor poetry install --no-root

run-dev:
	$(DEV_COMPOSE) up --build

run-dev-d:
	$(DEV_COMPOSE) up --build -d

display-dev:
	$(DEV_COMPOSE) run --rm plant-monitor python display_test.py

test-dev:
	$(DEV_COMPOSE) run --rm plant-monitor python -m compileall -q api display exceptions models services vendor web main.py display_test.py

docker-dev:
	$(DEV_COMPOSE) up --build

docker-dev-down:
	$(DEV_COMPOSE) down

docker-dev-display:
	$(DEV_COMPOSE) run --rm plant-monitor python display_test.py

install-pi:
	$(PI_COMPOSE) run --build --rm plant-monitor poetry install --no-root

run-pi:
	$(PI_COMPOSE) up --build

run-pi-d:
	$(PI_COMPOSE) up --build -d

display-pi:
	$(PI_COMPOSE) run --rm plant-monitor python display_test.py

docker-pi:
	$(PI_COMPOSE) up --build

docker-pi-down:
	$(PI_COMPOSE) down

docker-pi-display:
	$(PI_COMPOSE) run --rm plant-monitor python display_test.py
