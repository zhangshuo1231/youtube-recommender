import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import yaml

from analyzers import BaseAnalyzer, CommentAnalyzer
from youtube_service import YouTubeService


@dataclass
class ScoreBreakdown:
    """Breakdown of how the final score was calculated"""
    relevance: float = 0.0
    like_ratio: float = 0.0
    views: float = 0.0
    recency: float = 0.0
    duration_match: float = 0.0
    comment_quality: float = 0.0  # Reserved for future


@dataclass
class VideoRecommendation:
    """A recommended video with all its details"""
    video_id: str
    title: str
    channel: str
    thumbnail: str
    duration: str
    duration_seconds: int
    view_count: int
    like_count: int
    published_at: str
    score: float
    score_breakdown: ScoreBreakdown


class Recommender:
    """Video recommendation engine using configurable scoring weights"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.weights = self.config["scoring"]
        self.filters = self.config["filters"]
        self.duration_ranges = self.config["duration_ranges"]

        # Initialize analyzers
        self.analyzers: List[BaseAnalyzer] = []
        comment_config = self.config.get("comment_analysis", {})
        if comment_config.get("enabled", False):
            self.analyzers.append(CommentAnalyzer(enabled=True))

    def calculate_relevance_score(self, search_rank: int, max_results: int) -> float:
        """Calculate relevance score based on search ranking.

        Higher ranking (lower number) = higher score
        """
        if search_rank >= max_results:
            return 0.0
        return 1.0 - (search_rank / max_results)

    def calculate_like_ratio_score(self, view_count: int, like_count: int) -> float:
        """Calculate score based on view/like ratio.

        Lower ratio (more likes per view) = higher score
        """
        if like_count == 0:
            return 0.0

        ratio = view_count / like_count

        # Typical good ratio is around 20-50 (1 like per 20-50 views)
        # Excellent: < 20
        # Good: 20-50
        # Average: 50-100
        # Poor: > 100
        if ratio <= 20:
            return 1.0
        elif ratio <= 50:
            return 0.8 + (50 - ratio) / 150  # 0.8 to 1.0
        elif ratio <= 100:
            return 0.5 + (100 - ratio) / 100  # 0.5 to 0.8
        elif ratio <= 200:
            return 0.2 + (200 - ratio) / 500  # 0.2 to 0.5
        else:
            return max(0.1, 0.2 - (ratio - 200) / 1000)

    def calculate_view_score(self, view_count: int, all_view_counts: List[int]) -> float:
        """Calculate normalized view score using logarithmic scale.

        Uses log10 to prevent large channels from dominating.
        """
        if view_count <= 0:
            return 0.0

        log_views = math.log10(view_count + 1)

        # Normalize against max in the result set
        if all_view_counts:
            max_log = math.log10(max(all_view_counts) + 1)
            if max_log > 0:
                return log_views / max_log

        return min(1.0, log_views / 7)  # 10M views = log10(10^7) = 7

    def calculate_recency_score(self, published_at: str) -> float:
        """Calculate score based on how recent the video is.

        Newer videos get higher scores.
        """
        try:
            pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            now = datetime.now(pub_date.tzinfo)
            days_old = (now - pub_date).days

            if days_old <= 30:
                return 1.0
            elif days_old <= 90:
                return 0.9 - (days_old - 30) / 600  # 0.8 to 0.9
            elif days_old <= 365:
                return 0.7 - (days_old - 90) / 1100  # 0.45 to 0.7
            elif days_old <= 730:
                return 0.4 - (days_old - 365) / 1825  # 0.2 to 0.4
            else:
                return max(0.1, 0.2 - (days_old - 730) / 3650)
        except (ValueError, TypeError):
            return 0.5  # Default for unparseable dates

    def calculate_duration_match_score(
        self, duration_seconds: int, preference: Optional[str]
    ) -> float:
        """Calculate score based on duration matching user preference.

        Args:
            duration_seconds: Video duration in seconds
            preference: "short", "medium", "long", or "any"
        """
        if preference is None or preference == "any":
            return 1.0

        duration_minutes = duration_seconds / 60

        if preference == "short":
            max_minutes = self.duration_ranges["short"]["max_minutes"]
            if duration_minutes <= max_minutes:
                return 1.0
            elif duration_minutes <= max_minutes * 2:
                return 0.5
            return 0.2

        elif preference == "medium":
            min_minutes = self.duration_ranges["medium"]["min_minutes"]
            max_minutes = self.duration_ranges["medium"]["max_minutes"]
            if min_minutes <= duration_minutes <= max_minutes:
                return 1.0
            elif duration_minutes < min_minutes:
                return 0.7
            elif duration_minutes <= max_minutes * 1.5:
                return 0.6
            return 0.3

        elif preference == "long":
            min_minutes = self.duration_ranges["long"]["min_minutes"]
            if duration_minutes >= min_minutes:
                return 1.0
            elif duration_minutes >= min_minutes * 0.5:
                return 0.6
            return 0.3

        return 1.0

    def calculate_score(
        self,
        video: dict,
        search_rank: int,
        max_results: int,
        all_view_counts: List[int],
        duration_preference: Optional[str] = None,
    ) -> tuple[float, ScoreBreakdown]:
        """Calculate the final recommendation score for a video.

        Returns:
            Tuple of (total_score, score_breakdown)
        """
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        snippet = video.get("snippet", {})

        view_count = int(statistics.get("viewCount", 0))
        like_count = int(statistics.get("likeCount", 0))
        duration_str = content_details.get("duration", "PT0S")
        published_at = snippet.get("publishedAt", "")

        duration_seconds = YouTubeService.parse_duration(duration_str)

        # Calculate individual scores
        relevance = self.calculate_relevance_score(search_rank, max_results)
        like_ratio = self.calculate_like_ratio_score(view_count, like_count)
        views = self.calculate_view_score(view_count, all_view_counts)
        recency = self.calculate_recency_score(published_at)
        duration_match = self.calculate_duration_match_score(
            duration_seconds, duration_preference
        )

        # Apply weights
        breakdown = ScoreBreakdown(
            relevance=relevance * self.weights["relevance_weight"],
            like_ratio=like_ratio * self.weights["like_ratio_weight"],
            views=views * self.weights["view_count_weight"],
            recency=recency * self.weights["recency_weight"],
            duration_match=duration_match * self.weights["duration_match_weight"],
        )

        total_score = (
            breakdown.relevance
            + breakdown.like_ratio
            + breakdown.views
            + breakdown.recency
            + breakdown.duration_match
        )

        return total_score, breakdown

    def rank_videos(
        self,
        videos: List[dict],
        duration_preference: Optional[str] = None,
        top_n: Optional[int] = None,
    ) -> List[VideoRecommendation]:
        """Rank videos and return top recommendations.

        Args:
            videos: List of video data from YouTube API
            duration_preference: User's duration preference
            top_n: Number of recommendations to return (default from config)

        Returns:
            List of VideoRecommendation objects, sorted by score descending
        """
        if top_n is None:
            top_n = self.filters["final_recommendations"]

        max_results = self.filters["default_max_results"]

        # Collect all view counts for normalization
        all_view_counts = [
            int(v.get("statistics", {}).get("viewCount", 0)) for v in videos
        ]

        recommendations = []
        for video in videos:
            search_rank = video.get("search_rank", 999)
            score, breakdown = self.calculate_score(
                video=video,
                search_rank=search_rank,
                max_results=max_results,
                all_view_counts=all_view_counts,
                duration_preference=duration_preference,
            )

            snippet = video.get("snippet", {})
            statistics = video.get("statistics", {})
            content_details = video.get("contentDetails", {})

            duration_seconds = YouTubeService.parse_duration(
                content_details.get("duration", "PT0S")
            )

            rec = VideoRecommendation(
                video_id=video["id"],
                title=snippet.get("title", ""),
                channel=snippet.get("channelTitle", ""),
                thumbnail=snippet.get("thumbnails", {})
                .get("high", {})
                .get("url", ""),
                duration=YouTubeService.format_duration(duration_seconds),
                duration_seconds=duration_seconds,
                view_count=int(statistics.get("viewCount", 0)),
                like_count=int(statistics.get("likeCount", 0)),
                published_at=snippet.get("publishedAt", ""),
                score=round(score, 4),
                score_breakdown=breakdown,
            )
            recommendations.append(rec)

        # Sort by score descending
        recommendations.sort(key=lambda x: x.score, reverse=True)

        return recommendations[:top_n]
