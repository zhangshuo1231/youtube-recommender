import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeService:
    """Service for interacting with YouTube Data API v3"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key is required")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def search_videos(
        self,
        query: str,
        max_results: int = 15,
        published_after: Optional[datetime] = None,
        video_duration: Optional[str] = None,
    ) -> List[dict]:
        """Search for videos on YouTube.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            published_after: Only return videos published after this date
            video_duration: Filter by duration - "short" (<4min), "medium" (4-20min), "long" (>20min)

        Returns:
            List of video search results with basic info
        """
        search_params = {
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": max_results,
            "order": "relevance",
            "videoEmbeddable": "true",
        }

        if published_after:
            search_params["publishedAfter"] = published_after.isoformat() + "Z"

        if video_duration:
            search_params["videoDuration"] = video_duration

        try:
            response = self.youtube.search().list(**search_params).execute()
            return response.get("items", [])
        except HttpError as e:
            raise Exception(f"YouTube API error: {e}")

    def get_video_details(self, video_ids: List[str]) -> List[dict]:
        """Get detailed statistics for videos.

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            List of video details including statistics and content details
        """
        if not video_ids:
            return []

        try:
            response = (
                self.youtube.videos()
                .list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(video_ids),
                )
                .execute()
            )
            return response.get("items", [])
        except HttpError as e:
            raise Exception(f"YouTube API error: {e}")

    def search_and_get_details(
        self,
        query: str,
        max_results: int = 15,
        published_after: Optional[datetime] = None,
        video_duration: Optional[str] = None,
    ) -> List[dict]:
        """Search for videos and get their detailed statistics.

        This is a convenience method that combines search and details retrieval.

        Returns:
            List of videos with full details including statistics
        """
        search_results = self.search_videos(
            query=query,
            max_results=max_results,
            published_after=published_after,
            video_duration=video_duration,
        )

        if not search_results:
            return []

        video_ids = [item["id"]["videoId"] for item in search_results]
        video_details = self.get_video_details(video_ids)

        # Create a map of video_id to search rank
        rank_map = {item["id"]["videoId"]: idx for idx, item in enumerate(search_results)}

        # Add search rank to each video
        for video in video_details:
            video["search_rank"] = rank_map.get(video["id"], 999)

        return video_details

    @staticmethod
    def parse_duration(duration_str: str) -> int:
        """Parse ISO 8601 duration string to seconds.

        Args:
            duration_str: Duration in ISO 8601 format (e.g., "PT1H30M45S")

        Returns:
            Duration in seconds
        """
        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
        match = re.match(pattern, duration_str)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format seconds to human-readable duration string.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string like "1:30:45" or "15:30"
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    @staticmethod
    def get_published_after_date(time_range: str) -> Optional[datetime]:
        """Get the datetime for filtering by upload time.

        Args:
            time_range: "week", "month", "year", or "any"

        Returns:
            datetime object or None for "any"
        """
        now = datetime.utcnow()
        if time_range == "week":
            return now - timedelta(days=7)
        elif time_range == "month":
            return now - timedelta(days=30)
        elif time_range == "year":
            return now - timedelta(days=365)
        return None

    @staticmethod
    def get_published_after_from_months(max_months: Optional[int]) -> Optional[datetime]:
        """Get the datetime for filtering by maximum age in months.

        Args:
            max_months: Maximum age in months, or None for any time

        Returns:
            datetime object or None for "any"
        """
        if max_months is None:
            return None
        return datetime.utcnow() - timedelta(days=max_months * 30)
