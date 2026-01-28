from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalysisResult:
    """Result of video analysis"""
    score: float  # 0.0 to 1.0, higher is better
    flags: List[str] = field(default_factory=list)  # Detected issues
    reason: str = ""  # Human-readable explanation


class BaseAnalyzer(ABC):
    """Base class for all video analyzers.

    All analyzers must implement this interface to ensure
    consistent integration with the recommendation engine.
    """

    @abstractmethod
    async def analyze(self, video_id: str, video_data: dict) -> AnalysisResult:
        """Analyze a video and return the analysis result.

        Args:
            video_id: YouTube video ID
            video_data: Video metadata from YouTube API

        Returns:
            AnalysisResult containing:
                - score: 0.0-1.0, higher means better quality
                - flags: List of detected issue tags
                - reason: Human-readable analysis explanation
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Analyzer name for identification"""
        pass

    @property
    def is_enabled(self) -> bool:
        """Whether this analyzer is currently enabled"""
        return True
