"""JobMatch AI — compare a CV with a job offer using Claude."""

from .analyzer import MatchResult, analyze_match
from .cv_reader import read_cv

__all__ = ["MatchResult", "analyze_match", "read_cv"]
__version__ = "1.0.0"
