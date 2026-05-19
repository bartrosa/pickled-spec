"""pickled-iac: Terraform / OpenTofu drafting and verification."""

from pickled_iac.drafter import IaCDrafter
from pickled_iac.gates import IaCAmbiguityGate, PlanDiffGate, SecurityBaselineGate
from pickled_iac.oracle import validate
from pickled_iac.types import IaCArtifact, IaCToolMissingError, PlanResult, ValidateResult

__version__ = "0.1.0.dev0"

__all__ = [
    "IaCAmbiguityGate",
    "IaCArtifact",
    "IaCDrafter",
    "IaCToolMissingError",
    "PlanDiffGate",
    "PlanResult",
    "SecurityBaselineGate",
    "ValidateResult",
    "__version__",
    "validate",
]
