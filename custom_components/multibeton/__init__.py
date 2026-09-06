"""
Custom integration to integrate a Multibeton air-to-water heat-pump
controller with Home Assistant, over Modbus.

For more details about this integration, please refer to
https://github.com/YOUR_GITHUB_USERNAME/ha-multibeton
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.loader import async_get_loaded_integration

from .api import MultibetonApiClient
from .const import CONF_FRAMER, CONF_UNIT_ID, DOMAIN, LOGGER
from .coordinator import MultibetonDataUpdateCoordinator
from .data import MultibetonData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MultibetonConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
]

# The controller is polled directly over a local Modbus TCP link (typically
# an RTU-to-TCP gateway on the same network), so a short interval is cheap
# and keeps readings current - unlike a rate-limited cloud API.
SCAN_INTERVAL = timedelta(seconds=30)


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: MultibetonConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    client = MultibetonApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        unit_id=entry.data[CONF_UNIT_ID],
        framer=entry.data[CONF_FRAMER],
    )
    await client.async_connect()

    coordinator = MultibetonDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=SCAN_INTERVAL,
        config_entry=entry,
    )
    entry.runtime_data = MultibetonData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: MultibetonConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.client.async_close()
    return unloaded
