"""Compressor frequency-converter (inverter/VFD) telemetry, module 0.

Read from the input-register table (Modbus function code 0x04), the tail
block (addresses 1033-1046) of the "Anlageninformationen" sheet.
"""

from __future__ import annotations

from ..data_model import MultibetonComponent, gauge, integer


class Inverter(MultibetonComponent):
    """Compressor frequency-converter (inverter/VFD) telemetry, module 0."""

    register_space = "input"

    status_word = integer(
        1033,
        signed=False,
        maker_key="Hauptstatuswort Frequenzumrichter",
        description=(
            "Bitfeld, u.a. Bit0: einschaltbereit, Bit1: betriebsbereit "
            "(Rest teils reserviert/nicht vollständig dokumentiert)"
        ),
    )
    actual_speed = gauge(1034, 0.1, unit="rps", maker_key="Betriebsdrehzahl")
    module_temp = gauge(1035, 0.1, unit="°C", maker_key="Modultemperatur")
    output_power = gauge(1036, 0.01, unit="kW", maker_key="Ausgangsleistung")
    target_speed = gauge(1037, 0.1, unit="rps", maker_key="Solldrehzahl")
    output_current = gauge(1038, 0.1, unit="A", maker_key="Ausgangsstrom")
    output_torque = gauge(1039, 0.1, unit="%", maker_key="Ausgangsmoment")
    output_voltage = gauge(1040, 0.1, unit="V", maker_key="Ausgangsspannung")
    dc_bus_voltage = gauge(1041, 0.1, unit="V", maker_key="Zwischenkreisspannung")
    fault_code = integer(
        1042,
        maker_key="Störungscode",
        description=(
            "0 = keine Störung, sonst aktueller Störungscode des Frequenzumrichters"
        ),
    )
    input_current = gauge(
        1043,
        0.1,
        unit="A",
        maker_key="Eingangsstrom Frequenzumrichter",
    )
    pfc_temp = gauge(1044, 0.1, unit="°C", maker_key="PFC-Temperatur")
