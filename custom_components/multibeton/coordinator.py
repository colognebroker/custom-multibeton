"""DataUpdateCoordinator for multibeton."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MultibetonApiClientError

if TYPE_CHECKING:
    from .data import MultibetonConfigEntry
    from .multibeton_modbus.device import MultibetonHeatPump


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MultibetonDataUpdateCoordinator(DataUpdateCoordinator["MultibetonHeatPump"]):
    """Class to manage fetching data from the Multibeton controller."""

    config_entry: MultibetonConfigEntry

    async def _async_update_data(self) -> MultibetonHeatPump:
        """Update data via the vendored library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except MultibetonApiClientError as exception:
            raise UpdateFailed(str(exception)) from exception
