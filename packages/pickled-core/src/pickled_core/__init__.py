"""pickled-core: shared substrate of the pickled-* family."""

from pickled_core.gate import Gate
from pickled_core.llm import LLMClient, PromptTemplate
from pickled_core.types import (
    AmbiguityFinding,
    DraftResult,
    Feature,
    GateResult,
    Scenario,
    Verdict,
)

__version__ = "0.1.0.dev0"

__all__ = [
    "AmbiguityFinding",
    "DraftResult",
    "Feature",
    "Gate",
    "GateResult",
    "LLMClient",
    "PromptTemplate",
    "Scenario",
    "Verdict",
    "__version__",
]
