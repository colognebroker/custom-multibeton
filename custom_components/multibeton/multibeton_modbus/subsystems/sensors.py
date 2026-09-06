"""Module 0 compressor-circuit diagnostics and shared temperature sensors.

Read from the input-register table (Modbus function code 0x04), source
sheet "Analogwerte" of the manufacturer's register documentation.
"""

from __future__ import annotations

from ..data_model import MultibetonComponent, gauge, integer

# Sensor-absent/fault sentinel values documented on the "Analogwerte" sheet
# for every analog input, by their signed decimal meaning: -32700 = sensor
# not present, -32701 = sensor fault, -32702 = sensor open circuit,
# -32703 = sensor short circuit.
#
# A field's `nan` set is matched against the *raw* (unsigned 16-bit) register
# pattern before sign-folding (see modbus_connection.model.fields.NumberField
# .decode), so the signed sentinel values above must be converted to their
# two's-complement raw word form here - passing the negative decimals
# directly would never match and the sentinel would silently decode as a
# large negative temperature/pressure instead of ``None``.
_SENSOR_FAULT_SIGNED_CODES = (-32700, -32701, -32702, -32703)
SENSOR_FAULT_CODES = tuple(code & 0xFFFF for code in _SENSOR_FAULT_SIGNED_CODES)


class Sensors(MultibetonComponent):
    """Module 0 compressor-circuit diagnostics plus shared temperature sensors."""

    register_space = "input"

    main_expansion_valve_opening = integer(
        1301,
        unit="steps",
        maker_key="Öffnung Haupt-Expansionsventil",
    )
    aux_expansion_valve_opening = integer(
        1302,
        unit="steps",
        maker_key="Öffnung Zusatz-Expansionsventil",
    )
    fin_temp = gauge(
        1303,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Lamellentemperatur",
    )
    discharge_gas_temp = gauge(
        1304,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Heißgastemperatur",
    )
    suction_gas_temp = gauge(
        1305,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Sauggastemperatur",
    )
    after_valve_temp = gauge(
        1306,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Temperatur nach Ventil",
    )
    evaporation_saturation_temp = gauge(
        1308,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Verdampfungssättigungstemperatur",
    )
    condensation_saturation_temp = gauge(
        1309,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Kondensationssättigungstemperatur",
    )
    low_pressure = gauge(
        1310,
        0.1,
        unit="bar",
        nan=SENSOR_FAULT_CODES,
        maker_key="Niederdruck",
    )
    high_pressure = gauge(
        1311,
        0.1,
        unit="bar",
        nan=SENSOR_FAULT_CODES,
        maker_key="Hochdruck",
    )
    room_temp = gauge(
        3348,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Raumtemperatur",
        description="System resource column, not per-module.",
    )
    ambient_temp = gauge(
        3350,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Umgebungstemperatur",
        description="Outdoor temperature.",
    )
    dhw_tank_temp = gauge(
        3351,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Temperatur Warmwasserspeicher",
    )
    system_flow_temp = gauge(
        3353,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Gesamt-Vorlauftemperatur System",
    )
    solar_temp = gauge(
        3354,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Solartemperatur",
    )
    buffer_top_temp = gauge(
        3355,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Temperatur Pufferspeicher oben",
    )
    buffer_bottom_temp = gauge(
        3356,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Temperatur Pufferspeicher unten",
    )
    climate_flow_temp = gauge(
        3357,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Gesamt-Vorlauftemperatur Klimabetrieb",
    )
    floor_heating_flow_temp = gauge(
        3362,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Vorlauftemperatur Fußbodenheizung",
    )
    return_temp_zone_a = gauge(
        3376,
        0.1,
        unit="°C",
        nan=SENSOR_FAULT_CODES,
        maker_key="Rücklauftemperatur Zone A",
        description=(
            "Return-water temperature for climate zone A - pairs with "
            "climate_flow_temp/floor_heating_flow_temp for a flow/return "
            "reading. Documented on the 'Analogwerte' sheet's system-resource "
            "column (source label 'A区进水温度')."
        ),
    )
