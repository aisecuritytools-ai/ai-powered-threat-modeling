"""Markdown export for threat model results."""

from aitm.core.models import ThreatModelResult, Threat, RiskLevel


def export_markdown(result: ThreatModelResult) -> str:
    """Export threat model result as a Markdown report."""
    lines = []

    # Header
    lines.append("# Threat Model Report\n")
    lines.append(f"**Generated:** {result.metadata.get('timestamp', 'N/A')}")
    lines.append(f"**Model:** {result.metadata.get('model', 'N/A')}")
    lines.append(f"**Provider:** {result.metadata.get('provider', 'N/A')}")
    lines.append("")

    # Summary
    lines.append("## Summary\n")
    lines.append(result.summary)
    lines.append("")

    # Assets
    lines.append("## Assets\n")
    lines.append("| # | Asset | Type | Trust Boundary | Description |")
    lines.append("|---|-------|------|----------------|-------------|")
    for i, asset in enumerate(result.assets, 1):
        lines.append(
            f"| {i} | {asset.name} | {asset.type} | "
            f"{asset.trust_boundary or 'N/A'} | {asset.description} |"
        )
    lines.append("")

    # Data Flows
    if result.data_flows:
        lines.append("## Data Flows\n")
        lines.append("| Source | Target | Description | Protocol | Encrypted |")
        lines.append("|--------|--------|-------------|----------|-----------|")
        for flow in result.data_flows:
            encrypted = "✓" if flow.is_encrypted else "✗" if flow.is_encrypted is False else "?"
            lines.append(
                f"| {flow.source} | {flow.target} | {flow.description} | "
                f"{flow.protocol or 'N/A'} | {encrypted} |"
            )
        lines.append("")

    # Threats
    lines.append("## Threat Catalog\n")
    lines.append(f"**Total threats identified:** {len(result.threats)}\n")

    # Group by risk level
    risk_order = [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW, RiskLevel.MINIMAL]
    for risk in risk_order:
        risk_threats = [t for t in result.threats if t.risk_level == risk]
        if not risk_threats:
            continue

        emoji = _risk_emoji(risk)
        lines.append(f"### {emoji} {risk.value} Risk ({len(risk_threats)})\n")

        for threat in risk_threats:
            lines.append(f"#### [{threat.id}] {threat.name}\n")
            lines.append(f"- **STRIDE:** {threat.stride_category.value}")
            lines.append(f"- **Target:** {threat.target_asset}")
            lines.append(f"- **Impact:** {threat.impact} | **Likelihood:** {threat.likelihood}")
            if threat.attack_vector:
                lines.append(f"- **Attack Vector:** {threat.attack_vector}")
            if threat.cwe_id:
                lines.append(f"- **CWE:** {threat.cwe_id}")
            lines.append(f"\n{threat.description}\n")

            if threat.mitigations:
                lines.append("**Mitigations:**")
                for mit in threat.mitigations:
                    lines.append(f"- {mit.description}")
            lines.append("")

    # STRIDE distribution
    lines.append("## STRIDE Distribution\n")
    stride_counts = {}
    for threat in result.threats:
        cat = threat.stride_category.value
        stride_counts[cat] = stride_counts.get(cat, 0) + 1

    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat in ["Spoofing", "Tampering", "Repudiation", "Information Disclosure",
                "Denial of Service", "Elevation of Privilege"]:
        count = stride_counts.get(cat, 0)
        lines.append(f"| {cat} | {count} |")
    lines.append("")

    return "\n".join(lines)


def _risk_emoji(risk: RiskLevel) -> str:
    """Get emoji for risk level."""
    return {
        RiskLevel.CRITICAL: "🔴",
        RiskLevel.HIGH: "🟠",
        RiskLevel.MEDIUM: "🟡",
        RiskLevel.LOW: "🟢",
        RiskLevel.MINIMAL: "⚪",
    }.get(risk, "")
