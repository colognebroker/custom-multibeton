"""MultibetonEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DEVICE_MANUFACTURER, DEVICE_MODEL
from .coordinator import MultibetonDataUpdateCoordinator


class MultibetonEntity(CoordinatorEntity[MultibetonDataUpdateCoordinator]):
    """MultibetonEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: MultibetonDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            name=coordinator.config_entry.title,
        )
