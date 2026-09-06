"""Instantaneous electrical power consumption.

Read from the input-register table (Modbus function code 0x04); these rows
sit on the "Lesen-Schreiben" sheet but are documented read-only.
"""

from __future__ import annotations

from ..data_model import MultibetonComponent, integer


class Power(MultibetonComponent):
    """Instantaneous electrical power consumption."""

    register_space = "input"

    power_consumption = integer(
        5500,
        unit="W",
        maker_key="Aktuelle Leistungsaufnahme der Anlage",
        description=(
            "Tatsächliche Leistungsaufnahme der Anlage, ohne Zusatzheizstab "
            "und Speicher-Heizstab"
        ),
    )
    aux_heater_power = integer(
        5501,
        unit="W",
        maker_key="Aktuelle Leistung Zusatzheizstab",
    )
    aux_heater_power_configured = integer(
        5502,
        unit="W",
        maker_key="Konfigurierte Leistung Zusatzheizstab",
    )
