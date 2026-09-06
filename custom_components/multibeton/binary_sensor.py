"""Binary sensor platform for multibeton."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import MultibetonEntity
from .multibeton_modbus.enums import StatusFlags

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MultibetonDataUpdateCoordinator
    from .data import MultibetonConfigEntry


@dataclass(frozen=True, kw_only=True)
class MultibetonBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a binary sensor read from ``system_status``.

    Either derived from a bit of ``status_flags`` (set ``flag``) or from a
    plain boolean attribute on ``system_status`` (set ``attribute``).
    """

    flag: StatusFlags | None = None
    attribute: str | None = None


BINARY_SENSOR_DESCRIPTIONS: tuple[MultibetonBinarySensorEntityDescription, ...] = (
    MultibetonBinarySensorEntityDescription(
        key="problem",
        name="Problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        flag=StatusFlags.FAULT,
    ),
    MultibetonBinarySensorEntityDescription(
        key="defrosting",
        name="Defrosting",
        icon="mdi:snowflake-melt",
        flag=StatusFlags.DEFROSTING,
    ),
    MultibetonBinarySensorEntityDescription(
        key="frost_protection",
        name="Frost protection",
        device_class=BinarySensorDeviceClass.COLD,
        flag=StatusFlags.FROST_PROTECTION,
    ),
    MultibetonBinarySensorEntityDescription(
        key="floor_heating_present",
        name="Floor heating present",
        entity_category=EntityCategory.DIAGNOSTIC,
        attribute="floor_heating_present",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: MultibetonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        MultibetonBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in BINARY_SENSOR_DESCRIPTIONS
    )


class MultibetonBinarySensor(MultibetonEntity, BinarySensorEntity):
    """A binary sensor derived from ``system_status``."""

    entity_description: MultibetonBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: MultibetonDataUpdateCoordinator,
        entity_description: MultibetonBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary_sensor is on."""
        system_status = self.coordinator.data.system_status
        description = self.entity_description
        if description.flag is not None:
            status_flags = system_status.status_flags
            if status_flags is None:
                return None
            return description.flag in status_flags
        return getattr(system_status, description.attribute)
