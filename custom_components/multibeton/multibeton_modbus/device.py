"""The top-level Multibeton heat-pump device object."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import ModbusError
from modbus_connection.model import Component, ComponentGroup

from .exceptions import MultibetonWriteAccessError
from .subsystems import (
    Commands,
    Faults,
    HeatingCurve,
    HeatMeter,
    Inverter,
    Power,
    Sensors,
    SystemStatus,
    UserParameters,
)

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class MultibetonHeatPump:
    """A Multibeton X1.HL087A.K05.5032 air-to-water heat-pump controller.

    Owns a single ``modbus_connection.ModbusUnit`` and exposes the
    controller's curated Modbus datapoints as typed sub-components. The
    caller is responsible for building and connecting the underlying
    ``ModbusUnit`` (over TCP, a serial/RTU port, or an RTU-to-TCP gateway);
    this class only reads and writes through it.

    Models compressor-cascade module 0 only, the common single-module
    residential case; the controller's other modules (1#-7#) follow the same
    per-module register offset and are a natural extension via
    ``modbus_connection.model.repeating_group``, not implemented here.

    Example::

        from modbus_connection import ModbusTcpParams
        from modbus_connection.pymodbus import PymodbusConnection
        from multibeton_modbus import MultibetonHeatPump

        connection = PymodbusConnection(ModbusTcpParams(host="10.0.0.5"))
        await connection.connect()
        device = MultibetonHeatPump(connection.for_unit(1))
        await device.async_update()
        print(device.sensors.ambient_temp)
        await connection.close()
    """

    def __init__(self, unit: ModbusUnit) -> None:
        self._unit = unit
        self.system_status = SystemStatus(unit)
        self.sensors = Sensors(unit)
        self.inverter = Inverter(unit)
        self.power = Power(unit)
        self.faults = Faults(unit)
        self.commands = Commands(unit)
        self.heating_curve = HeatingCurve(unit)
        self.heat_meter = HeatMeter(unit)
        self.user_parameters = UserParameters(unit)
        self._group = ComponentGroup(unit, self.components)

    @property
    def modbus_unit(self) -> ModbusUnit:
        """The unit this device reads from and writes to."""
        return self._unit

    @property
    def components(self) -> tuple[Component, ...]:
        """Every subsystem this device refreshes in one pooled update."""
        return (
            self.system_status,
            self.sensors,
            self.inverter,
            self.power,
            self.faults,
            self.commands,
            self.heating_curve,
            self.heat_meter,
            self.user_parameters,
        )

    async def async_update(self) -> None:
        """Refresh every subsystem in pooled Modbus reads.

        Raises ``modbus_connection.ModbusExceptionError`` if the controller
        rejects a read block.
        """
        await self._group.async_update()

    async def async_write_command(self, field: str, value: bool) -> None:
        """Write one boolean command register on :attr:`commands`.

        A thin, friendlier wrapper around ``Commands.write`` that reports a
        failed controller write as :class:`MultibetonWriteAccessError`
        rather than letting the backend's raw ``ModbusError`` propagate
        unchanged - useful for a caller that wants one exception type
        regardless of the configured transport backend.

        Raises ``AttributeError`` for an unknown or read-only field and
        :class:`MultibetonWriteAccessError` if the write itself fails.
        """
        try:
            await self.commands.write(field, value)
        except ModbusError as err:
            raise MultibetonWriteAccessError(
                f"Could not write Multibeton command {field!r}"
            ) from err

    async def async_write_parameter(self, field: str, value: object) -> None:
        """Write one user-adjustable setpoint or mode field on :attr:`user_parameters`.

        Covers the "Benutzerparameter" register block (addresses 6400-6444):
        temperature setpoints (``int``), the disinfection schedule (``int``),
        module-enable flags (``bool``) and the mode/curve-selection enums
        (``int`` or the matching ``IntEnum``, e.g. :class:`~multibeton_modbus.enums.ConfiguredMode`).

        Raises ``AttributeError`` for an unknown or read-only field (for
        example ``fixed_curve_source``, which the source documentation marks
        factory/service level) and :class:`MultibetonWriteAccessError` if the
        write itself fails.
        """
        try:
            await self.user_parameters.write(field, value)
        except ModbusError as err:
            raise MultibetonWriteAccessError(
                f"Could not write Multibeton parameter {field!r}"
            ) from err
