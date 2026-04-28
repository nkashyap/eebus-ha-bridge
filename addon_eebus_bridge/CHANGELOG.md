# Changelog

## 0.1.10

- Register LPC and Monitoring use cases with the EEBUS service during startup (critical for remote entity compatibility resolution)
- Add startup confirmation log for use case registration

## 0.1.8

- Add automatic remote SKI re-registration when repeated monitoring/LPC reads return `NOT_FOUND`
- Improve HA coordinator recovery for bridge sessions that lose remote entity mapping after reconnects

## 0.1.7

- Preserve upstream gRPC status codes for monitoring reads (`NotFound` no longer rewrapped as `Internal`)
- Add debug flags for use-case callbacks to show whether incoming events include remote device/entity references

## 0.1.6

- Add compatibility fallback for monitoring reads when remote entity mapping is missing (`NOT_FOUND`) to recover power/energy values where possible
- Keep extensive debug telemetry for SKI registration, entity resolution, and polling summaries

## 0.1.5

- Add detailed HA-side and bridge-side monitoring debug logs for SKI registration, entity resolution, and read outcomes
- Fix pairing state debug formatting so connection state transitions render correctly in logs

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
