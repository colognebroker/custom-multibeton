"""Number platform for multibeton.

Covers the numeric ("Benutzerparameter", addresses 6400-6444) writable
setpoints on ``multibeton_modbus.subsystems.user_parameters.UserParameters`` -
the mode/curve-selection fields on the same component are select entities
instead, see ``select.py``.

Whether this address range is reachable through a given RTU-to-TCP gateway
has not been confirmed against real hardware; verify against the real
controller before relying on these entities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.exceptions import HomeAssistantError

from .api import MultibetonApiClientWriteError
from .entity import MultibetonEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MultibetonDataUpdateCoordinator
    from .data import MultibetonConfigEntry


@dataclass(frozen=True, kw_only=True)
class MultibetonNumberEntityDescription(NumberEntityDescription):
    """Describes a number backed by one writable ``user_parameters`` field."""

    field: str


NUMBER_DESCRIPTIONS: tuple[MultibetonNumberEntityDescription, ...] = (
    MultibetonNumberEntityDescription(
        key="cooling_setpoint_zone_a",
        name="Cooling setpoint",
        field="cooling_setpoint_zone_a",
        icon="mdi:snowflake-thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-15,
        native_max_value=35,
        native_step=1,
        mode=NumberMode.BOX,
    ),
    MultibetonNumberEntityDescription(
        key="heating_setpoint_zone_a",
        name="Heating setpoint",
        field="heating_setpoint_zone_a",
        icon="mdi:thermometer-plus",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0,
        native_max_value=85,
        native_step=1,
        mode=NumberMode.BOX,
    ),
    MultibetonNumberEntityDescription(
        key="dhw_setpoint",
        name="DHW setpoint",
        field="dhw_setpoint",
        icon="mdi:water-boiler",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0,
        native_max_value=80,
        native_step=1,
        mode=NumberMode.BOX,
    ),
    MultibetonNumberEntityDescription(
        key="cooling_room_setpoint_zone_a",
        name="Cooling room setpoint",
        field="cooling_room_setpoint_zone_a",
        icon="mdi:home-thermometer-outline",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=16,
        native_max_value=30,
        native_step=1,
        mode=NumberMode.BOX,
        entity_registry_enabled_default=False,
    ),
    MultibetonNumberEntityDescription(
        key="heating_room_setpoint_zone_a",
        name="Heating room setpoint",
        field="heating_room_setpoint_zone_a",
        icon="mdi:home-thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=16,
        native_max_value=30,
        native_step=1,
        mode=NumberMode.BOX,
        entity_registry_enabled_default=False,
    ),
    MultibetonNumberEntityDescription(
        key="cooling_setpoint_zone_b",
        name="Cooling setpoint (zone B)",
        field="cooling_setpoint_zone_b",
        icon="mdi:snowflake-thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-15,
        native_max_value=35,
        native_step=1,
        mode=NumberMode.BOX,
        entity_registry_enabled_default=False,
    ),
    MultibetonNumberEntityDescription(
        key="cooling_room_setpoint_zone_b",
        name="Cooling room setpoint (zone B)",
        field="cooling_room_setpoint_zone_b",
        icon="mdi:home-thermometer-outline",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=16,
        native_max_value=30,
        native_step=1,
        mode=NumberMode.BOX,
        entity_registry_enabled_default=False,
    ),
    MultibetonNumberEntityDescription(
        key="heating_setpoint_zone_b",
        name="Heating setpoint (zone B)",
        field="heating_setpoint_zone_b",
        icon="mdi:thermometer-plus",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0,
        native_max_value=85,
        native_step=1,
        mode=NumberMode.BOX,
        entity_registry_enabled_default=False,
    ),
    MultibetonNumberEntityDescription(
        key="heating_room_setpoint_zone_b",
        name="Heating room setpoint (zone B)",
        field="heating_room_setpoint_zone_b",
        icon="mdi:home-thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=16,
        native_max_value=30,
        native_step=1,
        mode=NumberMode.BOX,
        entity_registry_enabled_default=False,
    ),
    MultibetonNumberEntityDescription(
        key="disinfection_setpoint",
        name="Disinfection temperature",
        field="disinfection_setpoint",
        icon="mdi:biohazard",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=60,
        native_max_value=70,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="disinfection_max_interval_min",
        name="Disinfection max. interval",
        field="disinfection_max_interval_min",
        icon="mdi:timer-cog-outline",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=90,
        native_max_value=300,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="disinfection_hold_time_min",
        name="Disinfection hold time",
        field="disinfection_hold_time_min",
        icon="mdi:timer-cog-outline",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=5,
        native_max_value=60,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve_select_cooling_zone_a",
        name="Cooling curve selection (zone A)",
        field="curve_select_cooling_zone_a",
        icon="mdi:chart-bell-curve-cumulative",
        native_min_value=0,
        native_max_value=20,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve_select_heating_zone_a",
        name="Heating curve selection (zone A)",
        field="curve_select_heating_zone_a",
        icon="mdi:chart-bell-curve",
        native_min_value=0,
        native_max_value=20,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve_select_cooling_zone_b",
        name="Cooling curve selection (zone B)",
        field="curve_select_cooling_zone_b",
        icon="mdi:chart-bell-curve-cumulative",
        native_min_value=0,
        native_max_value=20,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve_select_heating_zone_b",
        name="Heating curve selection (zone B)",
        field="curve_select_heating_zone_b",
        icon="mdi:chart-bell-curve",
        native_min_value=0,
        native_max_value=20,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_cooling_ambient_1",
        name="Curve 9 (custom) cooling ambient temp. 1",
        field="curve9_cooling_ambient_1",
        icon="mdi:chart-bell-curve-cumulative",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-5,
        native_max_value=46,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_cooling_ambient_2",
        name="Curve 9 (custom) cooling ambient temp. 2",
        field="curve9_cooling_ambient_2",
        icon="mdi:chart-bell-curve-cumulative",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-5,
        native_max_value=46,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_cooling_outlet_1",
        name="Curve 9 (custom) cooling outlet temp. 1",
        field="curve9_cooling_outlet_1",
        icon="mdi:chart-bell-curve-cumulative",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5,
        native_max_value=25,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_cooling_outlet_2",
        name="Curve 9 (custom) cooling outlet temp. 2",
        field="curve9_cooling_outlet_2",
        icon="mdi:chart-bell-curve-cumulative",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5,
        native_max_value=25,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_heating_ambient_1",
        name="Curve 9 (custom) heating ambient temp. 1",
        field="curve9_heating_ambient_1",
        icon="mdi:chart-bell-curve",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-25,
        native_max_value=35,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_heating_ambient_2",
        name="Curve 9 (custom) heating ambient temp. 2",
        field="curve9_heating_ambient_2",
        icon="mdi:chart-bell-curve",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-25,
        native_max_value=35,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_heating_outlet_1",
        name="Curve 9 (custom) heating outlet temp. 1",
        field="curve9_heating_outlet_1",
        icon="mdi:chart-bell-curve",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=25,
        native_max_value=65,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonNumberEntityDescription(
        key="curve9_heating_outlet_2",
        name="Curve 9 (custom) heating outlet temp. 2",
        field="curve9_heating_outlet_2",
        icon="mdi:chart-bell-curve",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=25,
        native_max_value=65,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: MultibetonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        MultibetonNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in NUMBER_DESCRIPTIONS
    )


class MultibetonNumber(MultibetonEntity, NumberEntity):
    """A writable ``user_parameters`` setpoint register."""

    entity_description: MultibetonNumberEntityDescription

    def __init__(
        self,
        coordinator: MultibetonDataUpdateCoordinator,
        entity_description: MultibetonNumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def native_value(self) -> float | None:
        """Return the current setpoint."""
        return getattr(
            self.coordinator.data.user_parameters, self.entity_description.field
        )

    async def async_set_native_value(self, value: float) -> None:
        """Write the new setpoint to the controller."""
        try:
            await self.coordinator.config_entry.runtime_data.client.async_write_parameter(
                self.entity_description.field, int(value)
            )
        except MultibetonApiClientWriteError as exception:
            raise HomeAssistantError(str(exception)) from exception
        await self.coordinator.async_request_refresh()
