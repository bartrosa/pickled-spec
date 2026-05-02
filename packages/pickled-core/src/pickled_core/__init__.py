"""pickled-core: shared substrate of the pickled-* family."""

from pickled_core.gate import Gate
from pickled_core.llm import LLMClient, PromptTemplate
from pickled_core.mcp import (
    PickledMCPServer,
    ToolAlreadyRegisteredError,
    ToolRegistry,
)
from pickled_core.trace import (
    ArtifactKind,
    Citation,
    Confidence,
    Relation,
    Trace,
)
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
    "ArtifactKind",
    "Citation",
    "Confidence",
    "DraftResult",
    "Feature",
    "Gate",
    "GateResult",
    "LLMClient",
    "PickledMCPServer",
    "PromptTemplate",
    "Relation",
    "Scenario",
    "ToolAlreadyRegisteredError",
    "ToolRegistry",
    "Trace",
    "Verdict",
    "__version__",
]
