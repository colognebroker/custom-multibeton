# Vendored: `multibeton_modbus`

`custom_components/multibeton/multibeton_modbus/` is a **vendored, verbatim
copy** of the upstream [`multibeton-modbus`](https://github.com/multibeton-modbus/multibeton-modbus)
Python library's source tree (`src/multibeton_modbus/` in that project),
copied in as of this repository's snapshot of it.

## Why vendored instead of a normal pip requirement

`multibeton-modbus` has not been published to PyPI yet. A Home Assistant
custom integration installed through HACS cannot declare a `manifest.json`
`"requirements"` entry for a package that isn't installable from an index -
Home Assistant resolves `requirements` with `pip install`, which would fail
for every user until the package exists on PyPI. Vendoring the library's
source directly into the integration is the standard workaround the HACS
community uses to ship an integration ahead of its backend library's first
release: it lets this integration be installed and tested via HACS *today*,
with no dependency on a PyPI release or on a `home-assistant/core` PR
merging first.

The integration imports the vendored copy with ordinary relative imports,
e.g. from `custom_components/multibeton/__init__.py`:

```python
from .multibeton_modbus.device import MultibetonHeatPump
```

## What this means for `manifest.json`

Because the library is vendored, `multibeton-modbus` is deliberately **not**
listed in this integration's `manifest.json` `"requirements"`. Only the
library's own real runtime dependency - [`modbus-connection`](https://pypi.org/project/modbus-connection/),
which *is* published on PyPI - is listed there, pinned to the version range
`multibeton-modbus`'s own `pyproject.toml` declares.

## License

The upstream `multibeton-modbus` library is Apache-2.0 licensed (see
`multibeton_modbus/LICENSE`, copied in unmodified), distinct from this
integration repository's own MIT license (see `/LICENSE` at the repo root).
Apache-2.0 is permissive and compatible with redistribution inside an
MIT-licensed project; only the vendored subpackage's files fall under it.

## Keeping this copy in sync

This vendored copy is **not** automatically updated. If the upstream
`multibeton-modbus` library changes (bug fixes, new registers, corrected
scale factors, ...), someone must manually re-copy its `src/multibeton_modbus/`
tree into this directory and re-test.

## When to remove this vendored copy

Once `multibeton-modbus` is published to PyPI:

1. Delete this `multibeton_modbus/` subpackage.
2. Add `"multibeton-modbus==<version>"` to `manifest.json`'s
   `"requirements"` (alongside, or replacing, the `modbus-connection` pin as
   appropriate).
3. Change the vendored-relative imports (e.g.
   `from .multibeton_modbus.device import MultibetonHeatPump`) back to
   normal absolute imports (`from multibeton_modbus.device import
   MultibetonHeatPump`).

This is exactly the dependency this project's core-quality sibling
integration (`homeassistant/components/multibeton/`, built for
`home-assistant/core`) already uses - once vendoring is no longer necessary,
this custom integration can depend on the library the same way that one
does.
