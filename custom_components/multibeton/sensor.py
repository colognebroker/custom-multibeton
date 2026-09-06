"""Sensor platform for multibeton."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)

from .entity import MultibetonEntity
from .multibeton_modbus.enums import ConfiguredMode, CurrentMode, OperatingState

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MultibetonDataUpdateCoordinator
    from .data import MultibetonConfigEntry

# The five fully-documented fault/alarm bitfield registers curated by
# multibeton_modbus.subsystems.faults.Faults - see that module's docstring
# for the sparsely-documented words deliberately left out.
_FAULT_FIELDS = (
    "compressor_faults_1",
    "unit_faults_1",
    "unit_faults_2",
    "system_faults_1",
    "system_faults_6",
)


def _enum_options(enum_type: type[IntEnum]) -> list[str]:
    """Lower-cased option strings for a SensorDeviceClass.ENUM sensor."""
    return [member.name.lower() for member in enum_type]


@dataclass(frozen=True, kw_only=True)
class MultibetonSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor reading one attribute of one device subsystem."""

    component: str
    attribute: str


def _temperature(
    component: str, attribute: str, name: str, *, diagnostic: bool = True
) -> MultibetonSensorEntityDescription:
    return MultibetonSensorEntityDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC if diagnostic else None,
    )


def _pressure(component: str, attribute: str, name: str) -> MultibetonSensorEntityDescription:
    return MultibetonSensorEntityDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    )


def _runtime_minutes(
    component: str, attribute: str, name: str, *, total_increasing: bool
) -> MultibetonSensorEntityDescription:
    return MultibetonSensorEntityDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=(
            SensorStateClass.TOTAL_INCREASING
            if total_increasing
            else SensorStateClass.MEASUREMENT
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
    )


def _count(component: str, attribute: str, name: str) -> MultibetonSensorEntityDescription:
    return MultibetonSensorEntityDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
    )


def _power(
    component: str, attribute: str, name: str, unit: str, *, diagnostic: bool
) -> MultibetonSensorEntityDescription:
    return MultibetonSensorEntityDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=unit,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC if diagnostic else None,
    )


SENSOR_DESCRIPTIONS: tuple[MultibetonSensorEntityDescription, ...] = (
    # -- system_status -----------------------------------------------------
    MultibetonSensorEntityDescription(
        key="system_status_configured_mode",
        name="Configured mode",
        component="system_status",
        attribute="configured_mode",
        device_class=SensorDeviceClass.ENUM,
        options=_enum_options(ConfiguredMode),
        icon="mdi:thermostat",
    ),
    MultibetonSensorEntityDescription(
        key="system_status_current_mode",
        name="Current mode",
        component="system_status",
        attribute="current_mode",
        device_class=SensorDeviceClass.ENUM,
        options=_enum_options(CurrentMode),
        icon="mdi:thermostat",
    ),
    MultibetonSensorEntityDescription(
        key="system_status_operating_state",
        name="Operating state",
        component="system_status",
        attribute="operating_state",
        device_class=SensorDeviceClass.ENUM,
        options=_enum_options(OperatingState),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    _temperature(
        "system_status", "power_control_target_temp", "Power control target temperature"
    ),
    _temperature(
        "system_status", "power_control_actual_temp", "Power control actual temperature"
    ),
    MultibetonSensorEntityDescription(
        key="system_status_module_count",
        name="Module count",
        component="system_status",
        attribute="module_count",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
    ),
    _count("system_status", "defrost_count", "Defrost cycle count"),
    _count("system_status", "compressor_starts", "Compressor starts"),
    _count("system_status", "heating_starts", "Heating mode starts"),
    _count("system_status", "cooling_starts", "Cooling mode starts"),
    _count("system_status", "dhw_starts", "DHW mode starts"),
    _runtime_minutes(
        "system_status",
        "compressor_runtime_continuous_min",
        "Compressor continuous runtime",
        total_increasing=False,
    ),
    _runtime_minutes(
        "system_status",
        "compressor_idle_continuous_min",
        "Compressor continuous idle time",
        total_increasing=False,
    ),
    _runtime_minutes(
        "system_status",
        "compressor_runtime_total_min",
        "Compressor total runtime",
        total_increasing=True,
    ),
    _runtime_minutes(
        "system_status",
        "compressor_runtime_heating_min",
        "Compressor heating runtime",
        total_increasing=True,
    ),
    _runtime_minutes(
        "system_status",
        "compressor_runtime_cooling_min",
        "Compressor cooling runtime",
        total_increasing=True,
    ),
    _runtime_minutes(
        "system_status",
        "compressor_runtime_dhw_min",
        "Compressor DHW runtime",
        total_increasing=True,
    ),
    _runtime_minutes(
        "system_status",
        "aux_heater_runtime_min",
        "Auxiliary heater runtime",
        total_increasing=True,
    ),
    _runtime_minutes(
        "system_status",
        "tank_heater_runtime_min",
        "Tank heater runtime",
        total_increasing=True,
    ),
    # -- sensors -------------------------------------------------------------
    MultibetonSensorEntityDescription(
        key="sensors_main_expansion_valve_opening",
        name="Main expansion valve opening",
        component="sensors",
        attribute="main_expansion_valve_opening",
        native_unit_of_measurement="steps",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MultibetonSensorEntityDescription(
        key="sensors_aux_expansion_valve_opening",
        name="Auxiliary expansion valve opening",
        component="sensors",
        attribute="aux_expansion_valve_opening",
        native_unit_of_measurement="steps",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    _temperature("sensors", "fin_temp", "Fin temperature"),
    _temperature("sensors", "discharge_gas_temp", "Discharge gas temperature"),
    _temperature("sensors", "suction_gas_temp", "Suction gas temperature"),
    _temperature("sensors", "after_valve_temp", "Temperature after valve"),
    _temperature(
        "sensors", "evaporation_saturation_temp", "Evaporation saturation temperature"
    ),
    _temperature(
        "sensors", "condensation_saturation_temp", "Condensation saturation temperature"
    ),
    _pressure("sensors", "low_pressure", "Low pressure"),
    _pressure("sensors", "high_pressure", "High pressure"),
    _temperature("sensors", "room_temp", "Room temperature", diagnostic=False),
    _temperature("sensors", "ambient_temp", "Ambient temperature", diagnostic=False),
    _temperature("sensors", "dhw_tank_temp", "DHW tank temperature", diagnostic=False),
    _temperature(
        "sensors", "system_flow_temp", "System flow temperature", diagnostic=False
    ),
    _temperature("sensors", "solar_temp", "Solar temperature", diagnostic=False),
    _temperature(
        "sensors", "buffer_top_temp", "Buffer tank top temperature", diagnostic=False
    ),
    _temperature(
        "sensors",
        "buffer_bottom_temp",
        "Buffer tank bottom temperature",
        diagnostic=False,
    ),
    _temperature(
        "sensors", "climate_flow_temp", "Climate flow temperature", diagnostic=False
    ),
    _temperature(
        "sensors",
        "floor_heating_flow_temp",
        "Floor heating flow temperature",
        diagnostic=False,
    ),
    _temperature(
        "sensors",
        "return_temp_zone_a",
        "Zone A return temperature",
        diagnostic=False,
    ),
    # -- inverter --------------------------------------------------------------
    MultibetonSensorEntityDescription(
        key="inverter_status_word",
        name="Inverter status word",
        component="inverter",
        attribute="status_word",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chip",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="inverter_actual_speed",
        name="Inverter actual speed",
        component="inverter",
        attribute="actual_speed",
        native_unit_of_measurement="rps",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:fan",
    ),
    MultibetonSensorEntityDescription(
        key="inverter_target_speed",
        name="Inverter target speed",
        component="inverter",
        attribute="target_speed",
        native_unit_of_measurement="rps",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:fan",
    ),
    _temperature("inverter", "module_temp", "Inverter module temperature"),
    _temperature("inverter", "pfc_temp", "Inverter PFC temperature"),
    _power(
        "inverter",
        "output_power",
        "Inverter output power",
        UnitOfPower.KILO_WATT,
        diagnostic=True,
    ),
    MultibetonSensorEntityDescription(
        key="inverter_output_current",
        name="Inverter output current",
        component="inverter",
        attribute="output_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MultibetonSensorEntityDescription(
        key="inverter_input_current",
        name="Inverter input current",
        component="inverter",
        attribute="input_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MultibetonSensorEntityDescription(
        key="inverter_output_torque",
        name="Inverter output torque",
        component="inverter",
        attribute="output_torque",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MultibetonSensorEntityDescription(
        key="inverter_output_voltage",
        name="Inverter output voltage",
        component="inverter",
        attribute="output_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MultibetonSensorEntityDescription(
        key="inverter_dc_bus_voltage",
        name="Inverter DC bus voltage",
        component="inverter",
        attribute="dc_bus_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MultibetonSensorEntityDescription(
        key="inverter_fault_code",
        name="Inverter fault code",
        component="inverter",
        attribute="fault_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert-circle-outline",
    ),
    # -- power -----------------------------------------------------------------
    _power("power", "power_consumption", "Power consumption", UnitOfPower.WATT, diagnostic=False),
    _power(
        "power", "aux_heater_power", "Auxiliary heater power", UnitOfPower.WATT, diagnostic=False
    ),
    MultibetonSensorEntityDescription(
        key="power_aux_heater_power_configured",
        name="Auxiliary heater configured power",
        component="power",
        attribute="aux_heater_power_configured",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # -- heating_curve (read-only, no write function documented) --------------
    MultibetonSensorEntityDescription(
        key="heating_curve_heating_max_zone_a",
        name="Heating curve max (zone A)",
        component="heating_curve",
        attribute="heating_max_zone_a",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve",
    ),
    MultibetonSensorEntityDescription(
        key="heating_curve_heating_min_zone_a",
        name="Heating curve min (zone A)",
        component="heating_curve",
        attribute="heating_min_zone_a",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve",
    ),
    MultibetonSensorEntityDescription(
        key="heating_curve_cooling_max_zone_a",
        name="Cooling curve max (zone A)",
        component="heating_curve",
        attribute="cooling_max_zone_a",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve-cumulative",
    ),
    MultibetonSensorEntityDescription(
        key="heating_curve_cooling_min_zone_a",
        name="Cooling curve min (zone A)",
        component="heating_curve",
        attribute="cooling_min_zone_a",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve-cumulative",
    ),
    MultibetonSensorEntityDescription(
        key="heating_curve_heating_max_zone_b",
        name="Heating curve max (zone B)",
        component="heating_curve",
        attribute="heating_max_zone_b",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heating_curve_heating_min_zone_b",
        name="Heating curve min (zone B)",
        component="heating_curve",
        attribute="heating_min_zone_b",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heating_curve_cooling_max_zone_b",
        name="Cooling curve max (zone B)",
        component="heating_curve",
        attribute="cooling_max_zone_b",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve-cumulative",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heating_curve_cooling_min_zone_b",
        name="Cooling curve min (zone B)",
        component="heating_curve",
        attribute="cooling_min_zone_b",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chart-bell-curve-cumulative",
        entity_registry_enabled_default=False,
    ),
    # -- heat_meter (RAW/UNSCALED - see multibeton_modbus/subsystems/heat_meter.py) --
    # Disabled by default: these numbers are not yet in an engineering unit
    # (see the raw component's docstring), so showing them by default on a
    # dashboard would invite misreading a raw word as kWh/l/h. Enable them
    # in Settings -> Devices & services -> Multibeton -> entity list once you
    # want to inspect/calibrate them against real hardware.
    MultibetonSensorEntityDescription(
        key="heat_meter_heat_cumulative_raw",
        name="Heat meter cumulative heat (raw, unscaled)",
        component="heat_meter",
        attribute="heat_cumulative_raw",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heat_meter_flow_cumulative_raw",
        name="Heat meter cumulative flow (raw, unscaled)",
        component="heat_meter",
        attribute="flow_cumulative_raw",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heat_meter_flow_instant_raw",
        name="Heat meter instantaneous flow (raw, unscaled)",
        component="heat_meter",
        attribute="flow_instant_raw",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:gauge",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heat_meter_power_instant_raw",
        name="Heat meter instantaneous power (raw, unscaled)",
        component="heat_meter",
        attribute="power_instant_raw",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:gauge",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heat_meter_flow_temp_raw",
        name="Heat meter flow temperature (raw, unscaled)",
        component="heat_meter",
        attribute="flow_temp_raw",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heat_meter_return_temp_raw",
        name="Heat meter return temperature (raw, unscaled)",
        component="heat_meter",
        attribute="return_temp_raw",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
    ),
    MultibetonSensorEntityDescription(
        key="heat_meter_status",
        name="Heat meter status",
        component="heat_meter",
        attribute="status",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    ),
    # -- user_parameters (read-only field only, address 6416) -----------------
    # "Feste Kurvenquelle" carries factory/service ("Werk") permission in the
    # source table, not user permission, unlike every other Benutzerparameter
    # field - modeled read-only in the library (see subsystems/user_parameters.py)
    # and surfaced here as a diagnostic sensor rather than a number/select.
    MultibetonSensorEntityDescription(
        key="user_parameters_fixed_curve_source",
        name="Fixed curve source (factory)",
        component="user_parameters",
        attribute="fixed_curve_source",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:cog-outline",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: MultibetonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    entities: list[SensorEntity] = [
        MultibetonSensor(coordinator=coordinator, entity_description=description)
        for description in SENSOR_DESCRIPTIONS
    ]
    entities.append(MultibetonActiveFaultsSensor(coordinator=coordinator))
    async_add_entities(entities)


class MultibetonSensor(MultibetonEntity, SensorEntity):
    """A single value read from one attribute of one device subsystem."""

    entity_description: MultibetonSensorEntityDescription

    def __init__(
        self,
        coordinator: MultibetonDataUpdateCoordinator,
        entity_description: MultibetonSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def native_value(self) -> Any:
        """Return the current value, mapping enums to their lowercase name."""
        component = getattr(self.coordinator.data, self.entity_description.component)
        value = getattr(component, self.entity_description.attribute)
        if isinstance(value, IntEnum):
            return value.name.lower()
        return value


class MultibetonActiveFaultsSensor(MultibetonEntity, SensorEntity):
    """Summarizes which fault/alarm flags are currently active.

    Aggregates the five fully-documented fault-flag registers into one
    diagnostic sensor listing active flag names, rather than exposing one
    entity per bit (see multibeton_modbus.subsystems.faults for the register
    detail).
    """

    _attr_name = "Active faults"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator: MultibetonDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_active_faults"

    def _active_flag_names(self) -> list[str]:
        faults = self.coordinator.data.faults
        names: list[str] = []
        for field in _FAULT_FIELDS:
            value = getattr(faults, field)
            names.extend(f"{field}.{flag.name}" for flag in value)
        return names

    @property
    def native_value(self) -> str:
        """Return a short summary: 'none', or the count of active flags."""
        names = self._active_flag_names()
        return "none" if not names else f"{len(names)} active"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the full list of active flag names."""
        return {"active_faults": self._active_flag_names()}
