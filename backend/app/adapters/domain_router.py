"""
domain_router.py — Domain Adapter Factory (Auto-Discovery)
============================================================
Resolves a (domain, role) string pair into the correct BaseDomainAdapter
instance.

ADDING A NEW ROLE:
    1. Create a new file in adapters/ (e.g., healthcare_nurse.py)
    2. Define a class extending BaseDomainAdapter
    3. Done — the auto-discovery below will find it automatically.

NO EDITS TO THIS FILE ARE NEEDED WHEN ADDING ROLES.
"""
import importlib
import inspect
import pathlib
from typing import Dict, List

from .base_adapter import BaseDomainAdapter

# ── Auto-Discovery Engine ─────────────────────────────────────────────────────
# Scans all .py files in this package for BaseDomainAdapter subclasses
# and registers them by "domain:role" key.

_SKIP_FILES = {"__init__.py", "base_adapter.py", "domain_router.py"}


def _discover_adapters() -> Dict[str, BaseDomainAdapter]:
    """
    Scan every .py file in the adapters/ package, import it, and register
    any class that extends BaseDomainAdapter.

    Returns:
        Dict mapping "domain:role" keys to adapter instances.
        Example: {"healthcare:doctor": HealthcareAdapter(), ...}
    """
    registry: Dict[str, BaseDomainAdapter] = {}
    pkg_dir = pathlib.Path(__file__).parent

    for py_file in sorted(pkg_dir.glob("*.py")):
        if py_file.name in _SKIP_FILES:
            continue

        module = importlib.import_module(f".{py_file.stem}", package=__package__)

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(cls, BaseDomainAdapter)
                and cls is not BaseDomainAdapter
            ):
                instance = cls()
                key = (
                    f"{instance.get_domain_name().lower().strip()}"
                    f":{instance.get_role_name().lower().strip().replace(' ', '_')}"
                )
                registry[key] = instance

    return registry


# Build the registry once at import time
_ADAPTER_REGISTRY: Dict[str, BaseDomainAdapter] = _discover_adapters()

# ── Derived enum values exposed for FastAPI Query validation ───────────────────
VALID_DOMAINS: List[str] = sorted(
    {key.split(":")[0] for key in _ADAPTER_REGISTRY}
)
VALID_ROLES: List[str] = sorted(
    {key.split(":")[1] for key in _ADAPTER_REGISTRY}
)


def get_adapter(domain: str, role: str) -> BaseDomainAdapter:
    """
    Resolves a domain + role pair to the correct adapter instance.

    Args:
        domain: e.g. 'healthcare', 'it', 'education'
        role:   e.g. 'doctor', 'project_manager', 'tutor'

    Returns:
        The matching BaseDomainAdapter instance.

    Raises:
        ValueError if the domain/role combination is not registered.
    """
    key = f"{domain.lower().strip()}:{role.lower().strip()}"
    adapter = _ADAPTER_REGISTRY.get(key)
    if not adapter:
        raise ValueError(
            f"No adapter registered for domain='{domain}', role='{role}'. "
            f"Valid combinations: {list(_ADAPTER_REGISTRY.keys())}"
        )
    return adapter


def list_adapters() -> Dict[str, dict]:
    """
    Returns a summary of all registered adapters.
    Useful for debug endpoints and admin UIs.
    """
    return {
        key: adapter.to_context_dict()
        for key, adapter in _ADAPTER_REGISTRY.items()
    }
