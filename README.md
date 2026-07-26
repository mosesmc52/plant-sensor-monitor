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

View service logs with:

```bash
journalctl -u plant-monitor.service -f
```
