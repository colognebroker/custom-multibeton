# Multibeton Heat Pump for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A HACS-installable Home Assistant custom integration for a **Multibeton
X1.HL087A.K05.5032** air-to-water heat-pump controller (protocol version
V100C30), read and controlled over Modbus TCP (typically an RTU-to-TCP
gateway, since the controller is natively Modbus RTU).

This integration is built on top of the
[`multibeton-modbus`](https://github.com/multibeton-modbus/multibeton-modbus)
Python library, which curates a subset of the controller's Modbus register
map - comparable in breadth to the Luxtronik integration - covering overall
system status, temperature/pressure sensors, compressor inverter telemetry,
instantaneous power draw, grouped fault flags, and read-back-capable on/off
commands. See `custom_components/multibeton/multibeton_modbus/` (vendored
copy, see below) or the upstream project's README for the full register
list, including what is deliberately deferred.

## Why this integration vendorizes its library

`multibeton-modbus` has not been published to PyPI yet, and this
integration is meant to be installable and testable via HACS *today* -
before a PyPI release exists and before any `home-assistant/core` PR has
merged. So instead of listing `multibeton-modbus` as a `pip` requirement (a
package name that isn't installable from any index yet), this repository
copies the library's source directly into
`custom_components/multibeton/multibeton_modbus/` and imports it with
relative imports. See
[`custom_components/multibeton/VENDORED.md`](custom_components/multibeton/VENDORED.md)
for exactly what that means, how to keep the vendored copy in sync with
upstream, and how to drop it once a real PyPI release exists (this
project's sibling `home-assistant/core`-quality integration already depends
on the real package, and this one is meant to converge with it).

## Installation

### HACS (recommended)

1. In HACS, add this repository as a custom repository (category:
   Integration) - or, once accepted into the default HACS store, install it
   directly by searching for "Multibeton Heat Pump".
2. Restart Home Assistant.
3. Go to **Settings -> Devices & Services -> Add Integration**, search for
   "Multibeton Heat Pump", and follow the config flow.

### Manual

Copy `custom_components/multibeton/` into your Home Assistant `config/custom_components/` directory, restart Home Assistant, then add the integration through the UI as above.

## Configuration

Configuration is done entirely through the UI. You will need:

| Field | Meaning | Default |
| :--- | :--- | :--- |
| Host | Hostname or IP of the Modbus TCP gateway (or the controller itself, if it exposes Modbus TCP directly) | - |
| Port | TCP port | 502 |
| Modbus unit ID | Modbus RTU unit/station address behind the gateway | 1 |
| Wire framing | `rtu` (RTU-over-TCP, the expected setup for an RTU-to-TCP gateway) or `socket` (native Modbus TCP) | `rtu` |

Setup validates these by connecting and reading the controller once.

## What this integration exposes

* **Sensors** - all read-only numeric/enum datapoints: temperatures, pressures, valve positions, compressor inverter telemetry, instantaneous power draw (W), lifetime runtime/start counters, the read-only heating/cooling curve bounds, and the (raw/unscaled, disabled by default) heat meter block.
* **Binary sensors** - a `problem` indicator, plus `defrosting` and `frost_protection`, all derived from the controller's overall status-flags register; and `floor_heating_present`.
* **A diagnostic "Active faults" sensor** - summarizes which fault/alarm flag names are currently active across the five documented fault-flag registers, rather than one entity per bit; the full list is in its `active_faults` attribute.
* **Switches** - the persistent on/off commands (system on/off, zone A/B on/off, DHW on/off, forced DHW, scheduled disinfection, the two vacation modes), plus the "Benutzerparameter" boolean fields: a second, independent scheduled-disinfection enable and the per-module (00#-07#) enable flags (only module 0 enabled by default).
* **Buttons** - the momentary commands: reset fault, and start defrost.
* **Numbers** - the user-adjustable setpoints from the "Benutzerparameter" register block (addresses 6400-6444): cooling/heating/DHW setpoints and room-temperature setpoints for zones A and B, the disinfection temperature/interval/hold-time, the custom heating/cooling curve (curve 9) points, and the four curve-selection integers.
* **Selects** - the two mode fields from the same block: control mode (cool/heat/auto) and power mode (standard/boost/eco/auto).

**Important:** the "Benutzerparameter" registers (6400-6444) come from a
*different* manufacturer document than the rest of the curated register set
(see the `multibeton-modbus` library's README). Whether this address range
is actually reachable through your RTU-to-TCP gateway has **not been
confirmed against real hardware** - test carefully before relying on these
entities to control a running system.

## Known limitations

* **No single climate/water_heater entity.** Setpoints are exposed as
  individual `number`/`select` entities rather than grouped into one
  thermostat-style entity.
* **`manifest.json` intentionally lists only `modbus-connection`** (the
  vendored library's own real dependency) as a `requirements` entry - not a
  concrete Modbus backend (e.g. `pymodbus` or `tmodbus`). A concrete backend
  must also be present in Home Assistant's Python environment for this
  integration to actually talk to hardware; see
  `custom_components/multibeton/api.py` and
  `custom_components/multibeton/VENDORED.md`.
* **Placeholder `codeowners`/`documentation`/`issue_tracker` URLs** in
  `manifest.json` - update these before publishing.
* **Untested against real hardware or a live Home Assistant runtime.** This
  repository was built and statically verified (`py_compile`, JSON
  validation, import-resolution checks) outside of Home Assistant itself;
  it has not been exercised through HACS's install flow, `hassfest`, or a
  real controller.

## Development

This repository follows the
[`ludeeus/integration_blueprint`](https://github.com/ludeeus/integration_blueprint)
layout. See `scripts/setup` and `scripts/develop` to run a local Home
Assistant dev instance, and `scripts/lint` (ruff) for linting.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

This integration is MIT licensed - see [`LICENSE`](LICENSE). The vendored
`multibeton_modbus` subpackage is Apache-2.0 licensed by its upstream
project - see
[`custom_components/multibeton/VENDORED.md`](custom_components/multibeton/VENDORED.md).
