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
