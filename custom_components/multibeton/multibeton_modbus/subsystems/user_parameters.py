"""User-adjustable setpoints and mode selections ("Benutzerparameter").

Read and written through the holding-register table (Modbus function code
0x03 to read, 0x06 to write), source document "3-1 机型参数对照表" (model
parameter cross-reference table), group "用户参数" (Benutzerparameter),
addresses 6400-6444.

This is a *different* address range than the original curated register
table (which uses input registers 768-866 for read-only status and holding
registers 64000-64025 for commands): it comes from a separate manufacturer
document for the same controller model/firmware (protocol V100C30) and
documents the actual user-facing setpoints - cooling/heating/DHW target
temperatures, room-temperature setpoints, power mode, disinfection
schedule and heating-curve selection - that the original table did not
cover. Whether this range is reachable through a given RTU-to-TCP gateway
has not been confirmed against real hardware; verify against the real
controller before relying on these fields.

Two addresses in the source table are intentionally left out:

* 6411 - undocumented in the source (a genuine gap between "Leistungsmodus"
  and "Zeitgesteuerte Desinfektion", not a numbering error).
* 6417-6424 - a further undocumented gap (the source item numbering jumps
  from item 17 to item 26), most likely reserved/padding rather than a
  further extraction failure, but not modeled here since nothing is
  actually documented for these addresses.

``fixed_curve_source`` (6416) is modeled read-only even though it lives in
the "Benutzerparameter" address block: the source table marks its
permission level "厂家" (manufacturer/factory), not "用户" (user), unlike
every other field here.

The four curve-selection fields (6425-6428) accept 0-20 per the documented
range, but only value 0 ("禁用" / deaktiviert, i.e. disabled) is confirmed;
the source image for options 1-20 was cut off. Until the full option list
is available these are modeled as plain writable integers rather than an
``IntEnum``.
"""

from __future__ import annotations

from ..data_model import MultibetonComponent, boolean, enum, integer
from ..enums import ConfiguredMode, PowerMode


class UserParameters(MultibetonComponent):
    """User-adjustable setpoints and mode selections (addresses 6400-6444)."""

    register_space = "holding"

    control_mode = enum(
        6400,
        ConfiguredMode,
        writable=True,
        maker_key="Regelmodus",
        description="1: Kühlmodus; 2: Heizmodus; 3: Automatikmodus",
    )
    cooling_setpoint_zone_a = integer(
        6401,
        writable=True,
        unit="°C",
        maker_key="Kühlen Solltemperatur",
        description="Zone A, Vorlauf-Solltemperatur Kühlbetrieb. Bereich -15...35 °C.",
    )
    heating_setpoint_zone_a = integer(
        6402,
        writable=True,
        unit="°C",
        maker_key="Heizen Solltemperatur",
        description="Zone A, Vorlauf-Solltemperatur Heizbetrieb. Bereich 0...85 °C.",
    )
    dhw_setpoint = integer(
        6403,
        writable=True,
        unit="°C",
        maker_key="Warmwasser Solltemperatur",
        description="Bereich 0...80 °C.",
    )
    cooling_room_setpoint_zone_a = integer(
        6404,
        writable=True,
        unit="°C",
        maker_key="Kühlen Soll-Raumtemperatur",
        description="Zone A, nur bei Raumtemperaturregelung wirksam. Bereich 16...30 °C.",
    )
    heating_room_setpoint_zone_a = integer(
        6405,
        writable=True,
        unit="°C",
        maker_key="Heizen Soll-Raumtemperatur",
        description="Zone A, nur bei Raumtemperaturregelung wirksam. Bereich 16...30 °C.",
    )
    cooling_setpoint_zone_b = integer(
        6406,
        writable=True,
        unit="°C",
        maker_key="Kühlen Solltemperatur (B)",
        description="Zone B, Vorlauf-Solltemperatur Kühlbetrieb. Bereich -15...35 °C.",
    )
    cooling_room_setpoint_zone_b = integer(
        6407,
        writable=True,
        unit="°C",
        maker_key="Kühlen Soll-Raumtemperatur (B)",
        description="Zone B, nur bei Raumtemperaturregelung wirksam. Bereich 16...30 °C.",
    )
    heating_setpoint_zone_b = integer(
        6408,
        writable=True,
        unit="°C",
        maker_key="Heizen Solltemperatur (B)",
        description="Zone B, Vorlauf-Solltemperatur Heizbetrieb. Bereich 0...85 °C.",
    )
    heating_room_setpoint_zone_b = integer(
        6409,
        writable=True,
        unit="°C",
        maker_key="Heizen Soll-Raumtemperatur (B)",
        description="Zone B, nur bei Raumtemperaturregelung wirksam. Bereich 16...30 °C.",
    )
    power_mode = enum(
        6410,
        PowerMode,
        writable=True,
        maker_key="Leistungsmodus",
        description="0: Standard; 1: Kraftmodus; 2: Energiesparmodus; 3: Automatik",
    )
    # 6411 intentionally omitted - undocumented gap, see module docstring.
    disinfection_enabled = boolean(
        6412,
        writable=True,
        maker_key="Zeitgesteuerte Desinfektion",
        description=(
            "0: Deaktiviert; 1: Aktiviert. Eigenständiges Register von "
            "``Commands.scheduled_disinfection`` (Adresse 64022, "
            "ursprüngliche Registertabelle) - beide dokumentieren dieselbe "
            "Funktion 'Legionellenschutz', aber in unterschiedlichen "
            "Quelldokumenten mit unterschiedlicher Adresse."
        ),
    )
    disinfection_setpoint = integer(
        6413,
        writable=True,
        unit="°C",
        maker_key="Desinfektionstemperatur",
        description="Bereich 60...70 °C.",
    )
    disinfection_max_interval_min = integer(
        6414,
        writable=True,
        unit="min",
        maker_key="Max. Desinfektionsintervall",
        description="Bereich 90...300 min.",
    )
    disinfection_hold_time_min = integer(
        6415,
        writable=True,
        unit="min",
        maker_key="Desinfektion Haltezeit",
        description="Bereich 5...60 min.",
    )
    fixed_curve_source = integer(
        6416,
        writable=False,
        maker_key="Feste Kurvenquelle",
        description=(
            "Bereich 0...1. Berechtigungsstufe im Quelldokument 'Werk' "
            "(nicht 'Benutzer') - deshalb hier read-only modelliert, obwohl "
            "das Register im Adressblock der Benutzerparameter liegt."
        ),
    )
    # 6417-6424 intentionally omitted - undocumented gap, see module docstring.
    curve_select_cooling_zone_a = integer(
        6425,
        writable=True,
        maker_key="Zone A Kühlkurve",
        description=(
            "0: Deaktiviert; 1-20: Kurvenauswahl (volle Optionsliste in der "
            "Quelle nicht verfügbar, nur 0=Deaktiviert bestätigt)."
        ),
    )
    curve_select_heating_zone_a = integer(
        6426,
        writable=True,
        maker_key="Zone A Heizkurve",
        description=(
            "0: Deaktiviert; 1-20: Kurvenauswahl (volle Optionsliste in der "
            "Quelle nicht verfügbar, nur 0=Deaktiviert bestätigt)."
        ),
    )
    curve_select_cooling_zone_b = integer(
        6427,
        writable=True,
        maker_key="Zone B Kühlkurve",
        description=(
            "0: Deaktiviert; 1-20: Kurvenauswahl (volle Optionsliste in der "
            "Quelle nicht verfügbar, nur 0=Deaktiviert bestätigt)."
        ),
    )
    curve_select_heating_zone_b = integer(
        6428,
        writable=True,
        maker_key="Zone B Heizkurve",
        description=(
            "0: Deaktiviert; 1-20: Kurvenauswahl (volle Optionsliste in der "
            "Quelle nicht verfügbar, nur 0=Deaktiviert bestätigt)."
        ),
    )
    curve9_cooling_ambient_1 = integer(
        6429,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Kühlen Umgebungstemp. 1",
        description="Bereich -5...46 °C.",
    )
    curve9_cooling_ambient_2 = integer(
        6430,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Kühlen Umgebungstemp. 2",
        description="Bereich -5...46 °C.",
    )
    curve9_cooling_outlet_1 = integer(
        6431,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Kühlen Auslasstemp. 1",
        description="Bereich 5...25 °C.",
    )
    curve9_cooling_outlet_2 = integer(
        6432,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Kühlen Auslasstemp. 2",
        description="Bereich 5...25 °C.",
    )
    curve9_heating_ambient_1 = integer(
        6433,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Heizen Umgebungstemp. 1",
        description="Bereich -25...35 °C.",
    )
    curve9_heating_ambient_2 = integer(
        6434,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Heizen Umgebungstemp. 2",
        description="Bereich -25...35 °C.",
    )
    curve9_heating_outlet_1 = integer(
        6435,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Heizen Auslasstemp. 1",
        description="Bereich 25...65 °C.",
    )
    curve9_heating_outlet_2 = integer(
        6436,
        writable=True,
        unit="°C",
        maker_key="Kurve 9 (benutzerdefiniert) Heizen Auslasstemp. 2",
        description="Bereich 25...65 °C.",
    )
    module_0_enabled = boolean(
        6437,
        writable=True,
        maker_key="00# Modul-Einstellung",
    )
    module_1_enabled = boolean(
        6438,
        writable=True,
        maker_key="01# Modul-Einstellung",
    )
    module_2_enabled = boolean(
        6439,
        writable=True,
        maker_key="02# Modul-Einstellung",
    )
    module_3_enabled = boolean(
        6440,
        writable=True,
        maker_key="03# Modul-Einstellung",
    )
    module_4_enabled = boolean(
        6441,
        writable=True,
        maker_key="04# Modul-Einstellung",
    )
    module_5_enabled = boolean(
        6442,
        writable=True,
        maker_key="05# Modul-Einstellung",
    )
    module_6_enabled = boolean(
        6443,
        writable=True,
        maker_key="06# Modul-Einstellung",
    )
    module_7_enabled = boolean(
        6444,
        writable=True,
        maker_key="07# Modul-Einstellung",
    )
