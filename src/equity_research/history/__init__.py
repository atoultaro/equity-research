"""Provider-independent historical research; separate from execution replay."""

from .dataset import load_research_dataset

__all__ = ["load_research_dataset"]
