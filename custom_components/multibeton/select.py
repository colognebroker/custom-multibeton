"""Select platform for multibeton.

Covers the mode/curve-selection ("Benutzerparameter", addresses 6400-6444)
enum fields on ``multibeton_modbus.subsystems.user_parameters.UserParameters``
- the numeric setpoints on the same component are number entities instead,
see ``number.py``.

Whether this address range is reachable through a given RTU-to-TCP gateway
has not been confirmed against real hardware; verify against the real
controller before relying on these entities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.exceptions import HomeAssistantError

from .api import MultibetonApiClientWriteError
from .entity import MultibetonEntity
from .multibeton_modbus.enums import ConfiguredMode, PowerMode

if TYPE_CHECKING:
    from enum import IntEnum

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MultibetonDataUpdateCoordinator
    from .data import MultibetonConfigEntry

# Human-readable option labels, in enum declaration order, for each select's
# ``IntEnum``. ``current_option``/``async_select_option`` translate between
# these labels and the enum member the register actually stores.
_CONTROL_MODE_OPTIONS: dict[str, ConfiguredMode] = {
    "cool": ConfiguredMode.COOL,
    "heat": ConfiguredMode.HEAT,
    "auto": ConfiguredMode.AUTO,
}
_POWER_MODE_OPTIONS: dict[str, PowerMode] = {
    "standard": PowerMode.STANDARD,
    "boost": PowerMode.BOOST,
    "eco": PowerMode.ECO,
    "auto": PowerMode.AUTO,
}


@dataclass(frozen=True, kw_only=True)
class MultibetonSelectEntityDescription(SelectEntityDescription):
    """Describes a select backed by one writable ``user_parameters`` enum field."""

    field: str
    options_map: dict[str, IntEnum]


SELECT_DESCRIPTIONS: tuple[MultibetonSelectEntityDescription, ...] = (
    MultibetonSelectEntityDescription(
        key="control_mode",
        name="Control mode",
        field="control_mode",
        icon="mdi:sync",
        options=list(_CONTROL_MODE_OPTIONS),
        options_map=_CONTROL_MODE_OPTIONS,
    ),
    MultibetonSelectEntityDescription(
        key="power_mode",
        name="Power mode",
        field="power_mode",
        icon="mdi:speedometer",
        options=list(_POWER_MODE_OPTIONS),
        options_map=_POWER_MODE_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: MultibetonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        MultibetonSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in SELECT_DESCRIPTIONS
    )


class MultibetonSelect(MultibetonEntity, SelectEntity):
    """A writable ``user_parameters`` mode-selection register."""

    entity_description: MultibetonSelectEntityDescription

    def __init__(
        self,
        coordinator: MultibetonDataUpdateCoordinator,
        entity_description: MultibetonSelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._value_to_option = {
            value: option for option, value in entity_description.options_map.items()
        }

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        value = getattr(
            self.coordinator.data.user_parameters, self.entity_description.field
        )
        if value is None:
            return None
        return self._value_to_option.get(value)

    async def async_select_option(self, option: str) -> None:
        """Write the newly selected option to the controller."""
        value = self.entity_description.options_map[option]
        try:
            await self.coordinator.config_entry.runtime_data.client.async_write_parameter(
                self.entity_description.field, value
            )
        except MultibetonApiClientWriteError as exception:
            raise HomeAssistantError(str(exception)) from exception
        await self.coordinator.async_request_refresh()
