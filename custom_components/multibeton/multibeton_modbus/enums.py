"""Enumerations for the Multibeton heat-pump controller's Modbus datapoints.

Members are named after the documented meaning of each value or bit; a value
or bit position the manufacturer's register tables leave undocumented is
simply not given a name (a flag class keeps such bits, an ``IntEnum`` decodes
an undocumented value to ``None`` with a one-time warning).
"""

from __future__ import annotations

from enum import IntEnum, IntFlag


class ConfiguredMode(IntEnum):
    """User-configured operating mode (Anlagenstatus -> Eingestellter Modus)."""

    COOL = 1
    HEAT = 2
    AUTO = 3


class CurrentMode(IntEnum):
    """Actual operating mode the controller is currently running.

    Value 3 ("reserviert") is not documented and is intentionally omitted;
    the controller reading it decodes to ``None``.
    """

    NONE = 0
    COOLING = 1
    HEATING = 2
    DHW = 4


class PowerMode(IntEnum):
    """User-selected power/performance mode (Benutzerparameter -> Leistungsmodus)."""

    STANDARD = 0
    BOOST = 1
    ECO = 2
    AUTO = 3


class OperatingState(IntEnum):
    """Coarse system operating state (Betriebszustand)."""

    STANDBY = 0
    STARTING = 1
    RUNNING = 2
    SHUTTING_DOWN = 3
    SEVERE_ALARM = 4


class StatusFlags(IntFlag):
    """Bit flags of the overall system status word (Anlagenstatus)."""

    NONE = 0
    STANDBY = 1 << 0
    STARTING = 1 << 1
    RUNNING = 1 << 2
    SHUTTING_DOWN = 1 << 3
    SEVERE_ALARM = 1 << 4
    PREHEATING = 1 << 8
    FAULT = 1 << 9
    FROST_PROTECTION = 1 << 10
    DEFROSTING = 1 << 11


class CompressorFaults1(IntFlag):
    """Compressor-circuit fault bits, module 0 (Verdichterstörungen 1)."""

    NONE = 0
    LOW_PRESSURE = 1 << 0
    HIGH_PRESSURE = 1 << 1
    FIN_TEMP_FAULT = 1 << 4
    DISCHARGE_TEMP_FAULT = 1 << 5
    DISCHARGE_TEMP_TOO_HIGH = 1 << 6
    PRESSURE_SENSOR_J5_FAULT = 1 << 7
    PRESSURE_SENSOR_J6_FAULT = 1 << 8
    LOW_PRESSURE_TOO_LOW = 1 << 9
    HIGH_PRESSURE_TOO_HIGH = 1 << 10
    SUCTION_TEMP_FAULT = 1 << 11
    AFTER_VALVE_TEMP_FAULT = 1 << 12
    SUCTION_TEMP_TOO_LOW = 1 << 13
    EMERGENCY_DEFROST_TOO_FREQUENT = 1 << 14
    SUCTION_DISCHARGE_DIFF_IMPLAUSIBLE = 1 << 15


class UnitFaults1(IntFlag):
    """Heat-pump unit fault bits, group 1 (Einheitenstörungen 1)."""

    NONE = 0
    AMBIENT_TEMP_FAULT = 1 << 0
    COMMUNICATION_FAULT = 1 << 1
    EEPROM_DATA_ERROR = 1 << 2
    AUX_HEATER_OVERLOAD = 1 << 3
    PHE_FLOW_TEMP_TOO_LOW = 1 << 5
    PHE_FLOW_TEMP_TOO_HIGH = 1 << 6
    PHE_FLOW_TEMP_FAULT = 1 << 7
    FLOW_TOO_LOW = 1 << 8
    PHASE_LOSS_PROTECTION = 1 << 9
    PHE_RETURN_TEMP_FAULT = 1 << 10
    SYSTEM_FLOW_TEMP_FAULT = 1 << 11
    PHASE_SEQUENCE_PROTECTION = 1 << 12
    PHE_FLOW_RETURN_DIFF_TOO_LARGE = 1 << 13
    PHE_FLOW_RETURN_DIFF_IMPLAUSIBLE = 1 << 14
    INVERTER_PUMP_WARNING = 1 << 15


class UnitFaults2(IntFlag):
    """Heat-pump unit fault bits, group 2 (Einheitenstörungen 2)."""

    NONE = 0
    COMMUNICATION_ERROR = 1 << 0
    INDOOR_OUTDOOR_COMM_FAULT = 1 << 1
    PROTOCOL_VERSION_TOO_LOW = 1 << 2
    INVERTER_PUMP_FAULT = 1 << 3
    TYPE_SETTING_ERROR = 1 << 4
    R290_SENSOR_FAULT = 1 << 5
    R290_LEAK = 1 << 6
    FLOW_SENSOR_FAULT = 1 << 7
    WATER_PRESSURE_SENSOR_FAULT = 1 << 8
    INDOOR_OUTDOOR_COMM_ERROR = 1 << 9
    LED_BAR_COMM_FAULT = 1 << 10
    HEAT_METER_COMM_FAULT = 1 << 11
    ENERGY_METER_COMM_FAULT = 1 << 12


class SystemFaults1(IntFlag):
    """System-wide fault bits, group 1 (Systemstörungen 1)."""

    NONE = 0
    PHASE_SEQUENCE_PROTECTION = 1 << 1
    EEPROM_DATA_ERROR = 1 << 2
    CELL_TEMP_1_FAULT = 1 << 3
    CELL_TEMP_2_FAULT = 1 << 4
    SYSTEM_MAINTENANCE_DATA_ERROR = 1 << 6
    PHASE_LOSS_PROTECTION = 1 << 7
    TANK_HEATER_OVERLOAD = 1 << 10
    DHW_TANK_TEMP_FAULT = 1 << 12
    SYSTEM_FLOW_TEMP_FAULT = 1 << 14
    FLOOR_HEATING_FLOW_TEMP_FAULT = 1 << 15


class SystemFaults6(IntFlag):
    """System-wide fault bits, group 6 (Systemstörungen 6)."""

    NONE = 0
    BUFFER_TOP_TEMP_FAULT = 1 << 0
    BUFFER_BOTTOM_TEMP_FAULT = 1 << 1
    SOLAR_TEMP_FAULT = 1 << 2
    WIRED_REMOTE_COMM_FAULT = 1 << 3
    CLIMATE_FLOW_TEMP_FAULT = 1 << 4
    ROOM_TEMP_FAULT = 1 << 5
    SYSTEM_LOCKED_FREQUENT_STARTS = 1 << 7
    ZONE_A_RETURN_TEMP_FAULT = 1 << 9
