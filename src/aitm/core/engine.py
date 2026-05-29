"""Threat Modeling Engine — orchestrates the analysis workflow.

This is the core logic that can be consumed by:
- CLI (current)
- FastAPI backend (future)
- Lambda handler (future)
"""

import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from aitm.core.config import AITMConfig
from aitm.core.llm import create_llm, invoke_structured
from aitm.core.models import (
    Asset,
    DataFlow,
    Mitigation,
    RiskLevel,
    StrideCategory,
    Threat,
    ThreatModelResult,
)


# ─── Structured output schemas for LLM responses ───────────────────────────


class AssetList(BaseModel):
    """LLM response: list of identified assets."""
    assets: List[Asset] = Field(description="Assets identified in the architecture")


class DataFlowList(BaseModel):
    """LLM response: list of data flows."""
    data_flows: List[DataFlow] = Field(description="Data flows between assets")


class ThreatList(BaseModel):
    """LLM response: list of identified threats."""
    threats: List[Threat] = Field(description="Security threats identified")


# ─── Engine ─────────────────────────────────────────────────────────────────


class ThreatModelingEngine:
    """Main engine that runs the threat modeling workflow.

    Workflow:
    1. Analyze architecture → identify assets
    2. Identify data flows between assets
    3. Identify threats using STRIDE methodology
    4. Package results

    Designed to be stateless — all state is in the inputs/outputs.
    This makes it easy to wrap with any interface (CLI, API, Lambda).
    """

    def __init__(self, config: AITMConfig):
        self.config = config
        self.llm = create_llm(config)

    def run(
        self,
        description: str,
        image_path: Optional[Path] = None,
    ) -> ThreatModelResult:
        """Run the full threat modeling workflow.

        Args:
            description: System architecture description
            image_path: Optional path to architecture diagram

        Returns:
            ThreatModelResult with assets, flows, and threats
        """
        # Encode image if provided
        image_data = None
        if image_path:
            image_data = self._encode_image(image_path)

        # Step 1: Identify assets
        assets = self._identify_assets(description, image_data)

        # Step 2: Identify data flows
        data_flows = self._identify_data_flows(description, assets, image_data)

        # Step 3: Identify threats
        threats = self._identify_threats(description, assets, data_flows, image_data)

        # Package result
        return ThreatModelResult(
            summary=f"Threat model for system with {len(assets)} assets, "
                    f"{len(data_flows)} data flows, and {len(threats)} identified threats.",
            assets=assets,
            data_flows=data_flows,
            threats=threats,
            metadata={
                "provider": self.config.provider.value,
                "model": self.config.get_model_id(),
                "reasoning_level": self.config.reasoning_level,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "image_provided": image_path is not None,
            },
        )

    def _identify_assets(
        self, description: str, image_data: Optional[dict]
    ) -> List[Asset]:
        """Step 1: Identify assets and components in the architecture."""
        content = []

        if image_data:
            content.append(image_data)

        content.append({
            "type": "text",
            "text": f"""Analyze this system architecture and identify all assets/components.

SYSTEM DESCRIPTION:
{description}

For each asset, provide:
- name: Component name
- type: One of (web_app, api, database, message_queue, cache, cdn, load_balancer, 
  identity_provider, storage, serverless_function, container, external_service)
- description: What it does (1-2 sentences)
- trust_boundary: Which trust zone it belongs to (e.g., "Public Internet", 
  "DMZ", "Internal Network", "Data Layer")

Be thorough — include infrastructure components, not just application services.""",
        })

        messages = [
            SystemMessage(content="You are a security architect performing threat modeling. "
                         "Identify all components in the system architecture accurately."),
            HumanMessage(content=content),
        ]

        result = invoke_structured(self.llm, messages, AssetList)
        return result.assets

    def _identify_data_flows(
        self, description: str, assets: List[Asset], image_data: Optional[dict]
    ) -> List[DataFlow]:
        """Step 2: Identify data flows between assets."""
        asset_summary = "\n".join(
            f"- {a.name} ({a.type}): {a.description}" for a in assets
        )

        content = []
        if image_data:
            content.append(image_data)

        content.append({
            "type": "text",
            "text": f"""Identify all data flows between these assets.

SYSTEM DESCRIPTION:
{description}

IDENTIFIED ASSETS:
{asset_summary}

For each data flow, provide:
- source: Source asset name (must match an asset above)
- target: Target asset name (must match an asset above)
- description: What data flows (e.g., "User credentials for authentication")
- protocol: Communication protocol (HTTPS, gRPC, TCP, WebSocket, etc.)
- is_encrypted: Whether the flow is encrypted in transit

Focus on flows that cross trust boundaries — these are highest risk.""",
        })

        messages = [
            SystemMessage(content="You are a security architect mapping data flows for threat modeling. "
                         "Be thorough and identify all communication paths."),
            HumanMessage(content=content),
        ]

        result = invoke_structured(self.llm, messages, DataFlowList)
        return result.data_flows

    def _identify_threats(
        self,
        description: str,
        assets: List[Asset],
        data_flows: List[DataFlow],
        image_data: Optional[dict],
    ) -> List[Threat]:
        """Step 3: Identify threats using STRIDE methodology."""
        asset_summary = "\n".join(
            f"- {a.name} ({a.type}, boundary: {a.trust_boundary}): {a.description}"
            for a in assets
        )
        flow_summary = "\n".join(
            f"- {f.source} → {f.target}: {f.description} [{f.protocol or 'unknown'}]"
            for f in data_flows
        )

        content = []
        if image_data:
            content.append(image_data)

        content.append({
            "type": "text",
            "text": f"""Perform STRIDE threat analysis on this system.

SYSTEM DESCRIPTION:
{description}

ASSETS:
{asset_summary}

DATA FLOWS:
{flow_summary}

INSTRUCTIONS:
1. Apply STRIDE to each asset and data flow
2. Focus on threats that cross trust boundaries
3. For each threat provide:
   - id: Sequential number starting from 1
   - name: Short descriptive name (e.g., "SQL Injection in User API")
   - description: Detailed explanation (2-3 sentences)
   - stride_category: One of Spoofing, Tampering, Repudiation, Information Disclosure, 
     Denial of Service, Elevation of Privilege
   - target_asset: Which asset is targeted
   - risk_level: Critical, High, Medium, Low, or Minimal
   - impact: High, Medium, or Low
   - likelihood: High, Medium, or Low
   - mitigations: 2-4 specific, actionable mitigations
   - attack_vector: How the attack would be carried out
   - cwe_id: Related CWE if applicable (e.g., "CWE-89")

4. Aim for {self.config.max_threats} threats covering all STRIDE categories
5. Prioritize realistic, high-impact threats over theoretical ones
6. Each mitigation should be specific and actionable, not generic advice""",
        })

        messages = [
            SystemMessage(content="You are an expert security engineer performing STRIDE threat modeling. "
                         "Identify realistic, specific threats with actionable mitigations. "
                         "Cover all STRIDE categories proportionally."),
            HumanMessage(content=content),
        ]

        result = invoke_structured(self.llm, messages, ThreatList)
        return result.threats

    def _encode_image(self, image_path: Path) -> dict:
        """Encode image file to base64 for LLM consumption."""
        suffix = image_path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }

        mime_type = mime_map.get(suffix)
        if not mime_type:
            raise ValueError(f"Unsupported image format: {suffix}. Use PNG or JPEG.")

        image_bytes = image_path.read_bytes()
        b64_data = base64.b64encode(image_bytes).decode("utf-8")

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{b64_data}",
            },
        }
