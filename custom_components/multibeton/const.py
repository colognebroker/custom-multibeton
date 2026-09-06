"""Constants for multibeton."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "multibeton"
ATTRIBUTION = "Data provided by the Multibeton heat-pump controller via Modbus"

CONF_UNIT_ID = "unit_id"
CONF_FRAMER = "framer"

DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
# The controller is natively Modbus RTU; users typically reach it through an
# RTU-to-TCP gateway, so "rtu" (RTU-over-TCP framing) is the expected default
# rather than native Modbus TCP ("socket") framing.
DEFAULT_FRAMER = "rtu"

DEVICE_MANUFACTURER = "Multibeton"
DEVICE_MODEL = "X1.HL087A.K05.5032"
