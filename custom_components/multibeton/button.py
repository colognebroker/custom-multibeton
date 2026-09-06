"""Button platform for multibeton.

Covers the momentary (trigger-and-reset) command registers on
``multibeton_modbus.subsystems.commands.Commands`` - writing ``True`` starts
the action and the controller reports it back as ``0``/``False`` on the next
read once done, so these are represented as buttons rather than switches
(compare ``switch.py`` for the persistent on/off commands).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.exceptions import HomeAssistantError

from .api import MultibetonApiClientWriteError
from .entity import MultibetonEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MultibetonDataUpdateCoordinator
    from .data import MultibetonConfigEntry


@dataclass(frozen=True, kw_only=True)
class MultibetonButtonEntityDescription(ButtonEntityDescription):
    """Describes a button backed by one writable, momentary ``commands`` field."""

    field: str


BUTTON_DESCRIPTIONS: tuple[MultibetonButtonEntityDescription, ...] = (
    MultibetonButtonEntityDescription(
        key="reset_fault",
        name="Reset fault",
        field="reset_fault",
        icon="mdi:restart-alert",
    ),
    MultibetonButtonEntityDescription(
        key="defrost_command",
        name="Start defrost",
        field="defrost_command",
        icon="mdi:snowflake-melt",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: MultibetonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        MultibetonButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in BUTTON_DESCRIPTIONS
    )


class MultibetonButton(MultibetonEntity, ButtonEntity):
    """A momentary command register, triggered by writing ``True``."""

    entity_description: MultibetonButtonEntityDescription

    def __init__(
        self,
        coordinator: MultibetonDataUpdateCoordinator,
        entity_description: MultibetonButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    async def async_press(self) -> None:
        """Trigger the momentary command."""
        try:
            await self.coordinator.config_entry.runtime_data.client.async_write_command(
                self.entity_description.field, True  # noqa: FBT003
            )
        except MultibetonApiClientWriteError as exception:
            raise HomeAssistantError(str(exception)) from exception
        await self.coordinator.async_request_refresh()
