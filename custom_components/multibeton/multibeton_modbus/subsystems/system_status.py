"""Overall system state, operating mode, and lifetime run/start counters.

Read from the input-register table (Modbus function code 0x04), source
sheet "Anlageninformationen" of the manufacturer's register documentation.
"""

from __future__ import annotations

from ..data_model import (
    MultibetonComponent,
    boolean,
    enum,
    flags,
    gauge,
    integer,
    uint32,
)
from ..enums import ConfiguredMode, CurrentMode, OperatingState, StatusFlags


class SystemStatus(MultibetonComponent):
    """Overall system state, operating mode, and lifetime run/start counters."""

    register_space = "input"

    status_flags = flags(
        768,
        StatusFlags,
        maker_key="Anlagenstatus",
        description=(
            "B0: Anlage im Standby | B1: Anlage startet | B2: Anlage in Betrieb | "
            "B3: Anlage fährt herunter | B4: Anlage im schweren Alarmzustand | "
            "B8: Anlage im Vorwärmbetrieb | B9: Anlage hat eine Störung | "
            "B10: Anlage im Frostschutz | B11: Anlage im Abtaubetrieb"
        ),
    )
    configured_mode = enum(
        770,
        ConfiguredMode,
        maker_key="Eingestellter Modus",
        description="1: Kühlbetrieb; 2: Heizbetrieb; 3: Automatikbetrieb",
    )
    current_mode = enum(
        771,
        CurrentMode,
        maker_key="Aktueller Betriebsmodus",
        description="0: keiner; 1: Kühlen; 2: Heizen; 3: reserviert; 4: Warmwasser",
    )
    power_control_target_temp = gauge(
        772,
        0.1,
        unit="°C",
        maker_key="Zieltemperatur Leistungsregelung",
        description="Einheit 0,1 °C",
    )
    power_control_actual_temp = gauge(
        773,
        0.1,
        unit="°C",
        maker_key="Regeltemperatur Leistungsregelung",
        description="Einheit 0,1 °C",
    )
    module_count = integer(
        792,
        maker_key="Anzahl Module",
    )
    operating_state = enum(
        793,
        OperatingState,
        maker_key="Betriebszustand",
        description=(
            "0: Anlage im Standby; 1: Anlage startet; 2: Anlage in Betrieb; "
            "3: Anlage fährt herunter; 4: Anlage im schweren Alarmzustand"
        ),
    )
    floor_heating_present = boolean(
        866,
        maker_key="Flag Übergabesystem Fußbodenheizung",
        description=(
            "1, wenn das Übergabesystem in Zone A oder Zone B eine "
            "Fußbodenheizung ist, sonst 0"
        ),
    )
    defrost_count = uint32(
        840,
        maker_key="Anzahl Abtauvorgänge",
        description="High Word 840 / Low Word 841",
    )
    compressor_starts = uint32(
        842,
        maker_key="Anzahl Verdichterstarts",
        description="High Word 842 / Low Word 843",
    )
    heating_starts = uint32(
        844,
        maker_key="Anzahl Starts Heizbetrieb",
        description="High Word 844 / Low Word 845",
    )
    cooling_starts = uint32(
        846,
        maker_key="Anzahl Starts Kühlbetrieb",
        description="High Word 846 / Low Word 847",
    )
    dhw_starts = uint32(
        848,
        maker_key="Anzahl Starts Warmwasserbereitung",
        description="High Word 848 / Low Word 849",
    )
    compressor_runtime_continuous_min = uint32(
        850,
        unit="min",
        maker_key="Ununterbrochene Verdichterlaufzeit",
        description="High Word 850 / Low Word 851, Einheit Minuten",
    )
    compressor_idle_continuous_min = uint32(
        852,
        unit="min",
        maker_key="Ununterbrochene Verdichterstillstandszeit",
        description="High Word 852 / Low Word 853, Einheit Minuten",
    )
    compressor_runtime_total_min = uint32(
        854,
        unit="min",
        maker_key="Kumulierte Verdichterlaufzeit",
        description="High Word 854 / Low Word 855, Einheit Minuten",
    )
    compressor_runtime_heating_min = uint32(
        856,
        unit="min",
        maker_key="Kumulierte Verdichterlaufzeit Heizbetrieb",
        description="High Word 856 / Low Word 857",
    )
    compressor_runtime_cooling_min = uint32(
        858,
        unit="min",
        maker_key="Kumulierte Verdichterlaufzeit Kühlbetrieb",
        description="High Word 858 / Low Word 859",
    )
    compressor_runtime_dhw_min = uint32(
        860,
        unit="min",
        maker_key="Kumulierte Verdichterlaufzeit Warmwasserbereitung",
        description="High Word 860 / Low Word 861",
    )
    aux_heater_runtime_min = uint32(
        862,
        unit="min",
        maker_key="Laufzeit Zusatzheizstab",
        description="High Word 862 / Low Word 863",
    )
    tank_heater_runtime_min = uint32(
        864,
        unit="min",
        maker_key="Laufzeit Speicher-Heizstab",
        description="High Word 864 / Low Word 865",
    )
