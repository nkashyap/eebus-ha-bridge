#!/usr/bin/with-contenv bashio

set -euo pipefail

CFG_DIR="/config"
CFG_FILE="${CFG_DIR}/eebus-bridge.yaml"
CERT_DIR="/data/certs"

mkdir -p "${CFG_DIR}" "${CERT_DIR}"

cat >"${CFG_FILE}" <<EOF
grpc:
  port: $(bashio::config 'grpc_port')

eebus:
  port: $(bashio::config 'eebus_port')
  vendor: "$(bashio::config 'vendor')"
  brand: "$(bashio::config 'brand')"
  model: "$(bashio::config 'model')"
  serial: "$(bashio::config 'serial')"

certificates:
  auto_generate: $(bashio::config 'auto_generate_certificates')
  storage_path: "${CERT_DIR}"

logging:
  debug_events: $(bashio::config 'debug_events')
EOF

bashio::log.info "Generated bridge config at ${CFG_FILE}"
bashio::log.info "Starting eebus-bridge on gRPC port $(bashio::config 'grpc_port') and SHIP port $(bashio::config 'eebus_port')"

exec /usr/local/bin/eebus-bridge --config "${CFG_FILE}"
