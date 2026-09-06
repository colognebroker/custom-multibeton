"""Switch platform for multibeton.

Covers two kinds of persistent on/off style registers:

* the read-back-capable command registers on
  ``multibeton_modbus.subsystems.commands.Commands`` (the momentary
  trigger-and-reset commands ``reset_fault`` and ``defrost_command`` are
  button entities instead, see ``button.py``); and
* the boolean "Benutzerparameter" fields on
  ``multibeton_modbus.subsystems.user_parameters.UserParameters``
  (``disinfection_enabled`` and the per-module ``module_N_enabled`` flags,
  addresses 6412 and 6437-6444).

Both are written the same way from Home Assistant's point of view, but go
through different vendored-library write methods
(``async_write_command`` vs. ``async_write_parameter``), hence the
``component`` field on each description.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .api import MultibetonApiClientWriteError
from .entity import MultibetonEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MultibetonDataUpdateCoordinator
    from .data import MultibetonConfigEntry


@dataclass(frozen=True, kw_only=True)
class MultibetonSwitchEntityDescription(SwitchEntityDescription):
    """Describes a switch backed by one writable boolean register field."""

    field: str
    component: str = "commands"


SWITCH_DESCRIPTIONS: tuple[MultibetonSwitchEntityDescription, ...] = (
    MultibetonSwitchEntityDescription(
        key="system_on",
        name="System",
        field="system_on",
        icon="mdi:power",
    ),
    MultibetonSwitchEntityDescription(
        key="zone_a_on",
        name="Zone A",
        field="zone_a_on",
    ),
    MultibetonSwitchEntityDescription(
        key="zone_b_on",
        name="Zone B",
        field="zone_b_on",
    ),
    MultibetonSwitchEntityDescription(
        key="dhw_on",
        name="DHW",
        field="dhw_on",
        icon="mdi:water-boiler",
    ),
    MultibetonSwitchEntityDescription(
        key="forced_dhw",
        name="Forced DHW",
        field="forced_dhw",
        icon="mdi:water-boiler-alert",
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonSwitchEntityDescription(
        key="scheduled_disinfection",
        name="Scheduled disinfection",
        field="scheduled_disinfection",
        icon="mdi:biohazard",
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonSwitchEntityDescription(
        key="vacation_away",
        name="Vacation away",
        field="vacation_away",
        icon="mdi:bag-suitcase",
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonSwitchEntityDescription(
        key="vacation_home",
        name="Vacation home",
        field="vacation_home",
        icon="mdi:home-account",
        entity_category=EntityCategory.CONFIG,
    ),
    # -- user_parameters ("Benutzerparameter", address 6412) --
    MultibetonSwitchEntityDescription(
        key="disinfection_enabled",
        name="Scheduled disinfection (setpoint)",
        field="disinfection_enabled",
        component="user_parameters",
        icon="mdi:biohazard",
        entity_category=EntityCategory.CONFIG,
    ),
    # -- user_parameters ("Benutzerparameter", addresses 6437-6444) --
    # Only module 0 - the common single-module residential case this library
    # models - is enabled by default; modules 1-7 follow the same register
    # layout but are not otherwise implemented (see MultibetonHeatPump's
    # docstring), so they are exposed disabled unless the installation
    # actually has more than one module.
    MultibetonSwitchEntityDescription(
        key="module_0_enabled",
        name="Module 00# enabled",
        field="module_0_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
    ),
    MultibetonSwitchEntityDescription(
        key="module_1_enabled",
        name="Module 01# enabled",
        field="module_1_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    MultibetonSwitchEntityDescription(
        key="module_2_enabled",
        name="Module 02# enabled",
        field="module_2_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    MultibetonSwitchEntityDescription(
        key="module_3_enabled",
        name="Module 03# enabled",
        field="module_3_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    MultibetonSwitchEntityDescription(
        key="module_4_enabled",
        name="Module 04# enabled",
        field="module_4_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    MultibetonSwitchEntityDescription(
        key="module_5_enabled",
        name="Module 05# enabled",
        field="module_5_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    MultibetonSwitchEntityDescription(
        key="module_6_enabled",
        name="Module 06# enabled",
        field="module_6_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    MultibetonSwitchEntityDescription(
        key="module_7_enabled",
        name="Module 07# enabled",
        field="module_7_enabled",
        component="user_parameters",
        icon="mdi:developer-board",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: MultibetonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        MultibetonSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in SWITCH_DESCRIPTIONS
    )


class MultibetonSwitch(MultibetonEntity, SwitchEntity):
    """A persistent on/off register (a command or a user parameter)."""

    entity_description: MultibetonSwitchEntityDescription

    def __init__(
        self,
        coordinator: MultibetonDataUpdateCoordinator,
        entity_description: MultibetonSwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        component = getattr(self.coordinator.data, self.entity_description.component)
        return getattr(component, self.entity_description.field)

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self._async_write(value=True)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self._async_write(value=False)

    async def _async_write(self, *, value: bool) -> None:
        client = self.coordinator.config_entry.runtime_data.client
        write = (
            client.async_write_parameter
            if self.entity_description.component == "user_parameters"
            else client.async_write_command
        )
        try:
            await write(self.entity_description.field, value)
        except MultibetonApiClientWriteError as exception:
            raise HomeAssistantError(str(exception)) from exception
        await self.coordinator.async_request_refresh()
