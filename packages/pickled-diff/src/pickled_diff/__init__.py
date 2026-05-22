"""pickled-diff: differential oracle verification for the pickled-* family."""

from pickled_diff.comparator import Comparator, ExactEqComparator, StructuralJsonComparator
from pickled_diff.corpus import Corpus, InMemoryCorpus
from pickled_diff.gate import DifferentialOracleGate
from pickled_diff.runner import CallableRunner, OracleRunner, SubprocessRunner
from pickled_diff.types import DifferentialFinding, OracleOutput

from . import mcp_tools

__version__ = "0.1.0.dev0"

__all__ = [
    "CallableRunner",
    "Comparator",
    "Corpus",
    "DifferentialFinding",
    "DifferentialOracleGate",
    "ExactEqComparator",
    "InMemoryCorpus",
    "OracleOutput",
    "OracleRunner",
    "StructuralJsonComparator",
    "SubprocessRunner",
    "__version__",
    "mcp_tools",
]
