#!/usr/bin/env bash

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
expected_dir="/home/basil/plant-sensor-monitor"
service_name="plant-monitor.service"
service_source="$project_dir/system/$service_name"
service_target="/etc/systemd/system/$service_name"

if [[ "$project_dir" != "$expected_dir" ]]; then
    printf 'Error: this project must be located at %s\n' "$expected_dir" >&2
    printf 'Current location: %s\n' "$project_dir" >&2
    exit 1
fi

if [[ ! -f "$service_source" ]]; then
    printf 'Error: service file not found: %s\n' "$service_source" >&2
    exit 1
fi

if [[ "$EUID" -eq 0 ]]; then
    sudo_command=()
else
    sudo_command=(sudo)
fi

"${sudo_command[@]}" install -m 0644 "$service_source" "$service_target"
"${sudo_command[@]}" systemctl daemon-reload
"${sudo_command[@]}" systemctl enable --now "$service_name"

printf 'Installed and started %s\n' "$service_name"
printf 'View logs with: journalctl -u %s -f\n' "$service_name"
