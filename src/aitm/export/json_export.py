"""JSON export for threat model results."""

import json
from aitm.core.models import ThreatModelResult


def export_json(result: ThreatModelResult) -> str:
    """Export threat model result as formatted JSON."""
    return result.model_dump_json(indent=2)
