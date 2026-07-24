.PHONY: help install-dev run-dev display-dev test-dev \
	docker-dev docker-dev-down docker-dev-display \
	install-pi run-pi display-pi docker-pi docker-pi-down docker-pi-display \
	build up up-d down

POETRY ?= poetry
DOCKER_COMPOSE ?= docker compose
DEV_COMPOSE = $(DOCKER_COMPOSE) -f server/docker/docker-compose.dev.yml
PI_COMPOSE = $(DOCKER_COMPOSE) -f server/docker/docker-compose.pi.yml

help:
	@printf '%s\n' \
		'Local:' \
		'  make install-dev         Install Python dependencies for development' \
		'  make run-dev             Run the FastAPI server in development' \
		'  make display-dev         Render a development display preview' \
		'  make test-dev            Compile-check the server code' \
		'  make docker-dev          Build and run the development Docker service' \
		'  make docker-dev-down     Stop the development Docker service' \
		'' \
		'Raspberry Pi:' \
		'  make install-pi          Install dependencies on the Pi' \
		'  make run-pi              Run the FastAPI server on the Pi' \
		'  make display-pi           Update the physical Waveshare display' \
		'  make docker-pi           Build and run the Pi Docker service' \
		'  make docker-pi-down      Stop the Pi Docker service' \
		'  make docker-pi-display   Update the display from the Pi container'

install-dev:
	cd server && $(POETRY) install --no-root

run-dev:
	cd server && DISPLAY_BACKEND=preview $(POETRY) run python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

display-dev:
	cd server && DISPLAY_BACKEND=preview $(POETRY) run python display_test.py

test-dev:
	cd server && $(POETRY) run python -m compileall -q api display exceptions models services vendor web main.py display_test.py

docker-dev:
	$(DEV_COMPOSE) up --build

docker-dev-down:
	$(DEV_COMPOSE) down

docker-dev-display:
	$(DEV_COMPOSE) run --rm plant-monitor python display_test.py

install-pi:
	cd server && $(POETRY) install --no-root

run-pi:
	cd server && DISPLAY_BACKEND=waveshare $(POETRY) run python -m uvicorn main:app --host 0.0.0.0 --port 8000

display-pi:
	cd server && DISPLAY_BACKEND=waveshare $(POETRY) run python display_test.py

docker-pi:
	$(PI_COMPOSE) up --build

docker-pi-down:
	$(PI_COMPOSE) down

docker-pi-display:
	$(PI_COMPOSE) run --rm plant-monitor python display_test.py

# Backwards-compatible short aliases for the development container.
build:
	$(DEV_COMPOSE) build

up:
	$(DEV_COMPOSE) up

up-d:
	$(DEV_COMPOSE) up -d

down:
	$(DEV_COMPOSE) down
