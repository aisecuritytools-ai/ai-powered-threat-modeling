"""Data models for threat modeling results.

These models are the shared contract between CLI, future API, and future frontend.
Any consumer of the engine gets back these structured objects.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class StrideCategory(str, Enum):
    """STRIDE threat classification categories."""
    SPOOFING = "Spoofing"
    TAMPERING = "Tampering"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"


class RiskLevel(str, Enum):
    """Risk severity levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    MINIMAL = "Minimal"


class Asset(BaseModel):
    """An asset or component in the system architecture."""
    name: str = Field(description="Name of the asset/component")
    type: str = Field(description="Type (e.g., web_app, api, database, service)")
    description: str = Field(description="Brief description of the asset's purpose")
    trust_boundary: Optional[str] = Field(default=None, description="Trust boundary this asset belongs to")


class DataFlow(BaseModel):
    """A data flow between two assets."""
    source: str = Field(description="Source asset name")
    target: str = Field(description="Target asset name")
    description: str = Field(description="What data flows between them")
    protocol: Optional[str] = Field(default=None, description="Protocol used (HTTPS, gRPC, etc.)")
    is_encrypted: Optional[bool] = Field(default=None, description="Whether the flow is encrypted")


class Mitigation(BaseModel):
    """A recommended mitigation for a threat."""
    description: str = Field(description="What to do to mitigate the threat")
    priority: Optional[str] = Field(default=None, description="Implementation priority")


class Threat(BaseModel):
    """A security threat identified in the architecture."""
    id: int = Field(description="Unique threat identifier")
    name: str = Field(description="Short threat name")
    description: str = Field(description="Detailed threat description")
    stride_category: StrideCategory = Field(description="STRIDE classification")
    target_asset: str = Field(description="Which asset is targeted")
    risk_level: RiskLevel = Field(description="Overall risk level")
    impact: str = Field(description="Impact if exploited (High/Medium/Low)")
    likelihood: str = Field(description="Likelihood of exploitation (High/Medium/Low)")
    mitigations: List[Mitigation] = Field(default_factory=list, description="Recommended mitigations")
    attack_vector: Optional[str] = Field(default=None, description="How the attack would be carried out")
    cwe_id: Optional[str] = Field(default=None, description="Related CWE identifier")


class ThreatModelResult(BaseModel):
    """Complete threat modeling result — the output of the engine."""
    summary: str = Field(description="Brief summary of the system analyzed")
    assets: List[Asset] = Field(default_factory=list)
    data_flows: List[DataFlow] = Field(default_factory=list)
    threats: List[Threat] = Field(default_factory=list)
    assumptions: Optional[str] = Field(default=None, description="Assumptions made during analysis")
    metadata: dict = Field(default_factory=dict, description="Additional metadata (model, timestamp, etc.)")
