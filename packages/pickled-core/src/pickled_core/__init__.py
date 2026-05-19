"""pickled-core: shared substrate of the pickled-* family."""

from pickled_core.cost import CostBreakdown, PricingCatalogue, TokenUsage, estimate_cost
from pickled_core.gate import Gate
from pickled_core.llm import (
    Budget,
    BudgetExceededError,
    BudgetGuard,
    Completion,
    LLMClient,
    LLMError,
    Message,
    build_client,
    complete_prompt,
)
from pickled_core.llm import (
    TokenUsage as LLMTokenUsage,
)
from pickled_core.llm.prompts import PromptTemplate
from pickled_core.mcp import (
    PickledMCPServer,
    ToolAlreadyRegisteredError,
    ToolRegistry,
)
from pickled_core.telemetry import RunContext, current_run, generate_run_id, log_llm_call, start_run
from pickled_core.trace import (
    ArtifactKind,
    Confidence,
    Relation,
    SourceReference,
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
    "Budget",
    "BudgetExceededError",
    "BudgetGuard",
    "Completion",
    "Confidence",
    "CostBreakdown",
    "DraftResult",
    "Feature",
    "Gate",
    "GateResult",
    "LLMClient",
    "LLMError",
    "LLMTokenUsage",
    "Message",
    "PickledMCPServer",
    "PricingCatalogue",
    "PromptTemplate",
    "Relation",
    "RunContext",
    "Scenario",
    "SourceReference",
    "TokenUsage",
    "ToolAlreadyRegisteredError",
    "ToolRegistry",
    "Trace",
    "Verdict",
    "__version__",
    "build_client",
    "complete_prompt",
    "current_run",
    "estimate_cost",
    "generate_run_id",
    "log_llm_call",
    "start_run",
]
