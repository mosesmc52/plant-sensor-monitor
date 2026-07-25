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
