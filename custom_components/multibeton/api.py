"""Thin API client wrapping the vendored ``multibeton_modbus`` library.

Owns the Modbus TCP connection to the RTU-to-TCP gateway (or native Modbus
TCP device) and the vendored :class:`MultibetonHeatPump` device object built
on top of it. See ``multibeton_modbus/`` (vendored, see ``VENDORED.md``) for
the register-level detail and ``modbus_connection`` (a real pip requirement,
see ``manifest.json``) for the transport this client drives.

This integration owns its connection outright - unlike, say, an integration
that borrows a unit from a shared ``modbus_connection`` config entry - so a
config entry here maps to exactly one TCP connection to one gateway/device.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import ModbusError, ModbusTcpParams
from modbus_connection.tmodbus import TmodbusConnection

from .multibeton_modbus.device import MultibetonHeatPump
from .multibeton_modbus.exceptions import MultibetonWriteAccessError

if TYPE_CHECKING:
    from modbus_connection import ModbusConnection


class MultibetonApiClientError(Exception):
    """Exception to indicate a general API error."""


class MultibetonApiClientCommunicationError(MultibetonApiClientError):
    """Exception to indicate a communication (connect/read) error."""


class MultibetonApiClientWriteError(MultibetonApiClientError):
    """Exception to indicate a command-write error."""


class MultibetonApiClient:
    """Owns one Modbus TCP connection to a Multibeton controller."""

    def __init__(
        self,
        host: str,
        port: int,
        unit_id: int,
        framer: str = "rtu",
    ) -> None:
        """Build the connection and device object. Performs no I/O yet."""
        self._connection: ModbusConnection = TmodbusConnection(
            ModbusTcpParams(host=host, port=port, framer=framer),
        )
        self.device = MultibetonHeatPump(self._connection.for_unit(unit_id))

    async def async_connect(self) -> None:
        """Open the Modbus TCP connection.

        Raises :class:`MultibetonApiClientCommunicationError` if the
        connection cannot be established.
        """
        try:
            await self._connection.connect()
        except ModbusError as exception:
            msg = f"Could not connect to the Multibeton controller - {exception}"
            raise MultibetonApiClientCommunicationError(msg) from exception

    async def async_get_data(self) -> MultibetonHeatPump:
        """Refresh every subsystem and return the updated device.

        Raises :class:`MultibetonApiClientCommunicationError` if a read
        fails.
        """
        try:
            await self.device.async_update()
        except ModbusError as exception:
            msg = f"Error reading the Multibeton controller - {exception}"
            raise MultibetonApiClientCommunicationError(msg) from exception
        return self.device

    async def async_write_command(self, field: str, value: bool) -> None:
        """Write one boolean command register.

        Raises :class:`MultibetonApiClientWriteError` if the write fails.
        """
        try:
            await self.device.async_write_command(field, value)
        except MultibetonWriteAccessError as exception:
            msg = f"Could not write Multibeton command {field!r} - {exception}"
            raise MultibetonApiClientWriteError(msg) from exception

    async def async_write_parameter(self, field: str, value: object) -> None:
        """Write one user-adjustable setpoint or mode field ("Benutzerparameter").

        Raises :class:`MultibetonApiClientWriteError` if the write fails.
        """
        try:
            await self.device.async_write_parameter(field, value)
        except MultibetonWriteAccessError as exception:
            msg = f"Could not write Multibeton parameter {field!r} - {exception}"
            raise MultibetonApiClientWriteError(msg) from exception

    async def async_close(self) -> None:
        """Close the Modbus TCP connection permanently."""
        await self._connection.close()
