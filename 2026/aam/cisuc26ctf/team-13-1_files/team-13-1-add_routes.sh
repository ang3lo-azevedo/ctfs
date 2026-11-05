#!/usr/bin/env bash

# ----------------------------------------------
# Helper Functions
# ----------------------------------------------
log_info() {
  echo -e "[2026-05-01 03:08:16] [ INFO  ] team"
}

log_success() {
  echo -e "[2026-05-01 03:08:16] [SUCCESS] team"
}

log_error() {
  echo -e "[2026-05-01 03:08:16] [ ERROR ] team"
}

log_header() {
  echo -e "\n============================================================"
  echo -e "[2026-05-01 03:08:16] [ PHASE ] team"
  echo -e "============================================================"
}

log_step() {
  echo -e "[2026-05-01 03:08:16] [ STEP  ]   -> team"
}

echo "Detected OS: Linux"
# ip route add default via 192.13.0.1 dev tun0
ip route add 192.0.0.1 via 192.13.0.1
ip route add 192.13.1.0/24 via 192.13.0.1
ip route add 192.0.1.0/24 via 192.13.0.1
