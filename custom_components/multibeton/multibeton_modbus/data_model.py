"""Multibeton-specific wrapper layer over ``modbus_connection.model`` fields.

The ``modbus_connection.model`` field factories (``gauge()``, ``integer()``,
``boolean()``, ``enum()``, ``flags()``, ...) build typed register descriptors
but carry no notion of a manufacturer's own documentation. This module wraps
the handful of factories the Multibeton register map actually needs, adding
two pieces of descriptive metadata on top of each field:

* ``maker_key`` - the manufacturer's original German register name (e.g.
  ``"Anlagenstatus"``), letting a caller trace a datapoint back to the
  source register table.
* ``description`` - the manufacturer's German description of the register,
  copied from the source documentation.

Metadata is attached as a :class:`MultibetonMetadata` instance on the
field's ``multibeton_metadata`` attribute, so any caller - including
downstream applications built on top of this library - can introspect a
field's original manufacturer name and description without needing the
raw source spreadsheets. This layer intentionally stays thin: no write
validation, no unit conversion and no unlock sequences are added on top of
what ``modbus_connection.model`` already provides.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Any

from modbus_connection.model import (
    Component,
    boolean as _modbus_boolean,
    enum as _modbus_enum,
    flags as _modbus_flags,
    gauge as _modbus_gauge,
    integer as _modbus_integer,
    uint32 as _modbus_uint32,
)
from modbus_connection.model.fields import NumberField, WriteValidator

__all__ = [
    "MultibetonComponent",
    "MultibetonMetadata",
    "boolean",
    "enum",
    "flags",
    "gauge",
    "integer",
    "uint32",
]


@dataclass(frozen=True)
class MultibetonMetadata:
    """Manufacturer-facing metadata attached to one Multibeton datapoint.

    Attributes:
        maker_key: The manufacturer's original German register name, as
            printed in the source Modbus address table.
        description: The manufacturer's German description of the register,
            or an empty string where the source table gives none.
        unit: The physical unit of the decoded value, or ``None`` for a
            unitless, enum, flag or boolean datapoint.
    """

    maker_key: str
    description: str = ""
    unit: str | None = None


def _attach(field: Any, metadata: MultibetonMetadata) -> Any:
    """Attach Multibeton metadata to a ``modbus_connection`` field in place."""
    field.multibeton_metadata = metadata
    return field


def gauge(
    address: int,
    scale: float,
    *,
    maker_key: str,
    description: str = "",
    unit: str | None = None,
    **kwargs: Any,
) -> NumberField[float]:
    """Create a scaled numeric register field with Multibeton metadata."""
    field = _modbus_gauge(address, scale, unit=unit, **kwargs)
    return _attach(field, MultibetonMetadata(maker_key, description, unit))


def integer(
    address: int,
    *,
    maker_key: str,
    description: str = "",
    unit: str | None = None,
    **kwargs: Any,
) -> NumberField[int]:
    """Create an integer register field with Multibeton metadata."""
    field = _modbus_integer(address, unit=unit, **kwargs)
    return _attach(field, MultibetonMetadata(maker_key, description, unit))


def uint32(
    address: int,
    *,
    maker_key: str,
    description: str = "",
    unit: str | None = None,
    **kwargs: Any,
) -> NumberField[int]:
    """Create an unsigned 32-bit register field (two words, big-endian).

    ``modbus_connection.model.fields.uint32`` already combines the high and
    low words documented for a Multibeton runtime counter into one value
    when passed the field's single (high-word) address; this wrapper only
    adds Multibeton metadata on top.
    """
    field = _modbus_uint32(address, unit=unit, **kwargs)
    return _attach(field, MultibetonMetadata(maker_key, description, unit))


def boolean(
    address: int,
    *,
    maker_key: str,
    description: str = "",
    writable: bool | WriteValidator = False,
    **kwargs: Any,
) -> NumberField[bool]:
    """Create a 0/1 holding-register boolean field with Multibeton metadata."""
    field = _modbus_boolean(address, writable=writable, **kwargs)
    return _attach(field, MultibetonMetadata(maker_key, description, None))


def enum[E: IntEnum](
    address: int,
    enum_type: type[E],
    *,
    maker_key: str,
    description: str = "",
    **kwargs: Any,
) -> NumberField[E]:
    """Create a register field mapped to an ``IntEnum``, with metadata."""
    field = _modbus_enum(address, enum_type, **kwargs)
    return _attach(field, MultibetonMetadata(maker_key, description, None))


def flags[F: IntFlag](
    address: int,
    flag_type: type[F],
    *,
    maker_key: str,
    description: str = "",
    **kwargs: Any,
) -> NumberField[F]:
    """Create a register field mapped to an ``IntFlag``, with metadata."""
    field = _modbus_flags(address, flag_type, **kwargs)
    return _attach(field, MultibetonMetadata(maker_key, description, None))


class MultibetonComponent(Component):
    """Base class for Multibeton subsystems.

    Adds no behavior over ``modbus_connection.model.Component`` beyond a
    convenience lookup for the :class:`MultibetonMetadata` attached to each
    declared field by this module's field factories.
    """

    def metadata_for(self, field: str) -> MultibetonMetadata | None:
        """Return Multibeton metadata for a declared field, or ``None``."""
        descriptor = type(self).declared_fields.get(field)
        if descriptor is None:
            return None
        return getattr(descriptor, "multibeton_metadata", None)

    def require_metadata_for(self, field: str) -> MultibetonMetadata:
        """Return Multibeton metadata for a declared field.

        Raises ``AttributeError`` for an unknown or untyped field.
        """
        metadata = self.metadata_for(field)
        if metadata is None:
            raise AttributeError(f"unknown or untyped Multibeton field {field!r}")
        return metadata
