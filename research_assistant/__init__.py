"""research_assistant package initializer.

Expose core helpers at package level for convenient imports:

  from research_assistant import search_web, synthesize_findings

"""
from .research_assistant import (
    search_web,
    synthesize_findings,
)

__all__ = ["search_web", "synthesize_findings"]
