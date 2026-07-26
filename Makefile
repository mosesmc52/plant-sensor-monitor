.PHONY: help install-dev run-dev run-dev-d display-dev test-dev \
	docker-dev docker-dev-down docker-dev-display logs-dev \
	install-pi install-pi-service enable-pi-service disable-pi-service run-pi run-pi-d display-pi docker-pi docker-pi-down docker-pi-display \
	logs-pi install-pi-access-point enable-pi-access-point disable-pi-access-point enable-pi-wifi disable-pi-wifi \
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
		'  make logs-dev             Follow development Docker logs' \
		'' \
		'Raspberry Pi:' \
		'  make install-pi          Install dependencies in the Pi container' \
		'  make install-pi-service  Install the disabled systemd service' \
		'  make enable-pi-service   Enable and start the Pi systemd service' \
		'  make disable-pi-service  Stop and disable the Pi systemd service' \
		'  make run-pi              Run the FastAPI server in Docker on the Pi' \
		'  make run-pi-d            Run the FastAPI server in Docker on the Pi as a daemon' \
		'  make display-pi           Update the physical Waveshare display in Docker' \
		'  make docker-pi           Build and run the Pi Docker service' \
		'  make docker-pi-down      Stop the Pi Docker service' \
		'  make logs-pi              Follow Raspberry Pi Docker logs' \
		'  make install-pi-access-point Install the disabled Wi-Fi access point' \
		'  make enable-pi-access-point  Enable the Pi access point' \
		'  make disable-pi-access-point Disable the Pi access point' \
		'  make enable-pi-wifi          Enable the Pi Wi-Fi radio' \
		'  make disable-pi-wifi         Disable the Pi Wi-Fi radio' \
		'  make docker-pi-display   Update the display from the Pi container'

install-dev:
	$(DEV_COMPOSE) run --build --rm plant-monitor poetry install --no-root

up-dev:
	$(DEV_COMPOSE) up

up-dev-d:
	$(DEV_COMPOSE) up -d

display-dev:
	$(DEV_COMPOSE) run --rm plant-monitor python display_test.py

test-dev:
	$(DEV_COMPOSE) run --rm plant-monitor python -m compileall -q api display exceptions models services vendor web main.py display_test.py

build-dev:
	$(DEV_COMPOSE) build

down-dev:
	$(DEV_COMPOSE) down

docker-dev-display:
	$(DEV_COMPOSE) run --rm plant-monitor python display_test.py

logs-dev:
	$(DEV_COMPOSE) logs -f plant-monitor

install-pi:
	$(PI_COMPOSE) run --build --rm plant-monitor poetry install --no-root

install-pi-service:
	./scripts/install_plant_monitor_service.sh

enable-pi-service:
	sudo systemctl enable --now plant-monitor.service

disable-pi-service:
	sudo systemctl disable --now plant-monitor.service

up-pi:
	$(PI_COMPOSE) up

up-pi-d:
	$(PI_COMPOSE) up -d

display-pi:
	$(PI_COMPOSE) run --rm plant-monitor python display_test.py

build-pi:
	$(PI_COMPOSE) build

down-pi:
	$(PI_COMPOSE) down

docker-pi-display:
	$(PI_COMPOSE) run --rm plant-monitor python display_test.py

logs-pi:
	$(PI_COMPOSE) logs -f plant-monitor

install-pi-access-point:
	./scripts/install_plant_monitor_access_point.sh

enable-pi-access-point:
	sudo nmcli connection up id "$${AP_CONNECTION_NAME:-plant-monitor-access-point}" ifname "$${AP_INTERFACE:-wlan0}"

disable-pi-access-point:
	sudo nmcli connection down id "$${AP_CONNECTION_NAME:-plant-monitor-access-point}" || true

enable-pi-wifi:
	sudo nmcli radio wifi on

disable-pi-wifi:
	sudo nmcli radio wifi off
