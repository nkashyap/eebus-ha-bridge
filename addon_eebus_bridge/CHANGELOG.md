# Changelog

## 0.1.4

- Bump add-on and integration versions to force fresh Supervisor/HACS artifact resolution
- Keep runtime diagnostics improvements from 0.1.3

## 0.1.3

- Add explicit startup log lines for `debug_events` state to confirm debug logging is active at runtime
- Continue version alignment between add-on and custom integration

## 0.1.2

- Bump add-on and integration versions to align rebuilt artifacts with latest fixes
- Rename bridge sample runtime config to `bridge-config.yaml` to avoid Supervisor manifest parsing warnings

## 0.1.1

- Add optional `debug_events` add-on setting to trace inbound EEBUS callback/use-case events
- Improve runtime robustness and diagnostics paths in bridge and integration

## 0.1.0

- Initial Home Assistant add-on scaffold for the Go `eebus-bridge` service
