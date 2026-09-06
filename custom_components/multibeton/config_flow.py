"""Adds config flow for Multibeton."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import selector

from .api import MultibetonApiClient, MultibetonApiClientCommunicationError
from .const import (
    CONF_FRAMER,
    CONF_UNIT_ID,
    DEFAULT_FRAMER,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
    LOGGER,
)


class MultibetonFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Multibeton."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(
                    host=user_input[CONF_HOST],
                    port=user_input[CONF_PORT],
                    unit_id=user_input[CONF_UNIT_ID],
                    framer=user_input[CONF_FRAMER],
                )
            except MultibetonApiClientCommunicationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - surface anything unexpected as "unknown"
                LOGGER.exception("Unexpected error validating Multibeton connection")
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:"
                    f"{user_input[CONF_UNIT_ID]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Multibeton ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_PORT,
                        default=(user_input or {}).get(CONF_PORT, DEFAULT_PORT),
                    ): vol.All(
                        selector.NumberSelector(
                            selector.NumberSelectorConfig(
                                min=1,
                                max=65535,
                                mode=selector.NumberSelectorMode.BOX,
                            ),
                        ),
                        vol.Coerce(int),
                    ),
                    vol.Required(
                        CONF_UNIT_ID,
                        default=(user_input or {}).get(
                            CONF_UNIT_ID, DEFAULT_UNIT_ID
                        ),
                    ): vol.All(
                        selector.NumberSelector(
                            selector.NumberSelectorConfig(
                                min=1,
                                max=247,
                                mode=selector.NumberSelectorMode.BOX,
                            ),
                        ),
                        vol.Coerce(int),
                    ),
                    vol.Required(
                        CONF_FRAMER,
                        default=(user_input or {}).get(CONF_FRAMER, DEFAULT_FRAMER),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=["rtu", "socket"],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_connection(
        self,
        host: str,
        port: int,
        unit_id: int,
        framer: str,
    ) -> None:
        """Validate the connection by connecting and reading the device once."""
        client = MultibetonApiClient(
            host=host,
            port=port,
            unit_id=unit_id,
            framer=framer,
        )
        try:
            await client.async_connect()
            await client.async_get_data()
        finally:
            await client.async_close()
