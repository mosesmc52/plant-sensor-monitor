#!/usr/bin/env bash

set -euo pipefail

connection_name="${AP_CONNECTION_NAME:-plant-monitor-access-point}"
interface_name="${AP_INTERFACE:-wlan0}"
ap_ssid="${AP_SSID:-PlantMonitor}"
ap_address="${AP_ADDRESS:-192.168.50.1/24}"
ap_hostname="${AP_HOSTNAME:-greenhouse}"

if ! command -v nmcli >/dev/null 2>&1; then
    printf 'Error: nmcli is required. Install or enable NetworkManager first.\n' >&2
    exit 1
fi

if [[ "$EUID" -eq 0 ]]; then
    sudo_command=()
else
    sudo_command=(sudo)
fi

if ! command -v avahi-daemon >/dev/null 2>&1; then
    "${sudo_command[@]}" apt-get update
    "${sudo_command[@]}" apt-get install -y avahi-daemon
fi

if command -v hostnamectl >/dev/null 2>&1; then
    "${sudo_command[@]}" hostnamectl set-hostname "$ap_hostname"
else
    printf 'Error: hostnamectl is required to configure mDNS hostname.\n' >&2
    exit 1
fi

"${sudo_command[@]}" systemctl enable --now avahi-daemon

if [[ -z "${AP_PASSWORD:-}" ]]; then
    read -r -s -p "Access point password (8+ characters): " ap_password
    printf '\n'
else
    ap_password="$AP_PASSWORD"
fi

if (( ${#ap_password} < 8 )); then
    printf 'Error: the access point password must be at least 8 characters.\n' >&2
    exit 1
fi

if "${sudo_command[@]}" nmcli connection show "$connection_name" >/dev/null 2>&1; then
    "${sudo_command[@]}" nmcli connection modify "$connection_name" \
        802-11-wireless.ssid "$ap_ssid" \
        802-11-wireless.mode ap \
        802-11-wireless.band bg \
        connection.interface-name "$interface_name" \
        connection.autoconnect no \
        ipv4.method shared \
        ipv4.addresses "$ap_address" \
        ipv6.method disabled \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.psk "$ap_password"
else
    "${sudo_command[@]}" nmcli connection add \
        type wifi \
        ifname "$interface_name" \
        con-name "$connection_name" \
        autoconnect no \
        ssid "$ap_ssid"

    "${sudo_command[@]}" nmcli connection modify "$connection_name" \
        802-11-wireless.mode ap \
        802-11-wireless.band bg \
        ipv4.method shared \
        ipv4.addresses "$ap_address" \
        ipv6.method disabled \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.psk "$ap_password"
fi

# Keep installation disabled and do not interrupt an existing network.
"${sudo_command[@]}" nmcli connection down id "$connection_name" >/dev/null 2>&1 || true

printf 'Installed access point profile: %s\n' "$connection_name"
printf 'SSID: %s\n' "$ap_ssid"
printf 'Pi address: %s\n' "${ap_address%/*}"
printf 'mDNS hostname: %s.local\n' "$ap_hostname"
printf 'The profile is disabled by default.\n'
printf 'Enable it with: make enable-pi-access-point\n'
