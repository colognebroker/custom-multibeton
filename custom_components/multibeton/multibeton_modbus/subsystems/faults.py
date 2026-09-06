"""Grouped fault/alarm bitfields, module 0 and system-wide.

Read from the input-register table (Modbus function code 0x04), source
sheet "04-Stoerungen". Only the fully-documented words are modeled here;
sparsely-documented words (``compressor_faults_2``/``compressor_faults_3``,
most of ``system_faults_2`` through ``system_faults_5``) are deliberately
left out for a future extension - see the project README.
"""

from __future__ import annotations

from ..data_model import MultibetonComponent, flags
from ..enums import (
    CompressorFaults1,
    SystemFaults1,
    SystemFaults6,
    UnitFaults1,
    UnitFaults2,
)


class Faults(MultibetonComponent):
    """Grouped fault/alarm bitfields, module 0 and system-wide."""

    register_space = "input"

    compressor_faults_1 = flags(
        1294,
        CompressorFaults1,
        maker_key="Verdichterstörungen 1",
    )
    unit_faults_1 = flags(
        1298,
        UnitFaults1,
        maker_key="Einheitenstörungen 1",
    )
    unit_faults_2 = flags(
        1299,
        UnitFaults2,
        maker_key="Einheitenstörungen 2",
    )
    system_faults_1 = flags(
        3342,
        SystemFaults1,
        maker_key="Systemstörungen 1",
    )
    system_faults_6 = flags(
        3347,
        SystemFaults6,
        maker_key="Systemstörungen 6",
    )
