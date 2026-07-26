#!/usr/bin/env bash

set -euo pipefail

preview_url="${PREVIEW_URL:-http://localhost:8000/api/v1/readings}"
device_id="${DEVICE_ID:-preview-plant}"
reading_number="${READING_NUMBER:-1}"
temperature_f="${TEMPERATURE_F:-72}"
humidity_percent="${HUMIDITY_PERCENT:-50}"
light_lux="${LIGHT_LUX:-500}"
moisture_percent="${MOISTURE_PERCENT:-60}"
uptime_seconds="${UPTIME_SECONDS:-1}"

curl --fail --silent --show-error \
  -X POST "$preview_url" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$device_id\",
    \"reading_number\": $reading_number,
    \"temperature_f\": $temperature_f,
    \"humidity_percent\": $humidity_percent,
    \"light_lux\": $light_lux,
    \"moisture_1_percent\": $moisture_percent,
    \"uptime_seconds\": $uptime_seconds
  }"

printf '\nPreview image: server/output/display.png\n'
