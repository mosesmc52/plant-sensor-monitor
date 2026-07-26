# plant-sensor-monitor

## Raspberry Pi display setup

Enable SPI on the Raspberry Pi before starting the display container:

```text
sudo raspi-config
Interface Options
└── SPI
    └── Enable
```

Then reboot the Raspberry Pi:

```bash
sudo reboot
```

## Display sensor statistics

Sensor statistics are displayed by default. To hide temperature, moisture,
and light values, set this environment variable for the server:

```text
DISPLAY_SENSOR_STATS=false
```

## Start automatically on Raspberry Pi boot

The Pi service starts after networking and Docker are ready, then launches
the Waveshare display container:

```bash
cd /home/basil/plant-sensor-monitor
./scripts/install_plant_monitor_service.sh
```

The service is disabled by default. Enable and start it explicitly when
needed:

```bash
make enable-pi-service
```

View service logs with:

```bash
journalctl -u plant-monitor.service -f
```

## Firmware Wi-Fi credentials

Keep firmware credentials out of GitHub. For each firmware project, create the
local configuration header from its example, then edit it with your Wi-Fi
details:

```bash
cd firmware/plant_sensor_node_simulator
cp wifi_config.h.example wifi_config.h

cd ../plant_sensor_node
cp wifi_config.h.example wifi_config.h
```

The real `wifi_config.h` is ignored by Git. If the old credentials were ever
uploaded, rotate that Wi-Fi password because removing it from the latest file
does not remove it from Git history.
