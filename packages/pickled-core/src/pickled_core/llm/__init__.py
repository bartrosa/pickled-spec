"""LLM client abstraction.

`LLMClient` is the protocol every drafter and gate consumes. The Anthropic
reference implementation lives in `anthropic.py` and is an OPTIONAL
dependency: install with `pip install pickled-core[anthropic]`.

`PromptTemplate` is a tiny `.md` loader with `{{var}}` substitution. It
intentionally does not implement Jinja or any other templating language —
prompts that need conditionals belong in code, not templates.
"""

from pickled_core.llm.client import LLMClient
from pickled_core.llm.prompts import PromptTemplate

__all__ = ["LLMClient", "PromptTemplate"]
