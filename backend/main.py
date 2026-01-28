import os
from dataclasses import asdict
from typing import List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from recommender import Recommender, VideoRecommendation
from youtube_service import YouTubeService

load_dotenv()

app = FastAPI(
    title="YouTube Tutorial Recommender",
    description="Search and recommend YouTube video tutorials based on quality metrics",
    version="1.0.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
youtube_service: Optional[YouTubeService] = None
recommender: Optional[Recommender] = None


def get_youtube_service() -> YouTubeService:
    global youtube_service
    if youtube_service is None:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="YouTube API key not configured"
            )
        youtube_service = YouTubeService(api_key)
    return youtube_service


def get_recommender() -> Recommender:
    global recommender
    if recommender is None:
        recommender = Recommender()
    return recommender


class SearchRequest(BaseModel):
    """Request body for video search"""
    technology: str = Field(..., min_length=1, max_length=100, description="Technology name (e.g., Python, React, Docker)")
    level: Optional[Literal["beginner", "intermediate", "advanced"]] = Field(
        default=None,
        description="Skill level: beginner, intermediate, advanced, or None for any"
    )
    duration_preference: Literal["short", "medium", "long", "any"] = Field(
        default="any",
        description="Preferred video duration: short (<10min), medium (10-30min), long (>30min), any"
    )
    max_months: Optional[int] = Field(
        default=None,
        ge=1,
        le=60,
        description="Maximum age of video in months (1-60), None for any time"
    )

    def build_query(self) -> str:
        """Build YouTube search query from structured parameters"""
        parts = [self.technology, "tutorial"]
        if self.level:
            level_terms = {
                "beginner": "beginner",
                "intermediate": "intermediate",
                "advanced": "advanced"
            }
            parts.append(level_terms[self.level])
        return " ".join(parts)


class ScoreBreakdownResponse(BaseModel):
    """Score breakdown in API response"""
    relevance: float
    like_ratio: float
    views: float
    recency: float
    duration_match: float


class VideoResponse(BaseModel):
    """Video recommendation in API response"""
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
    score_breakdown: ScoreBreakdownResponse


class SearchResponse(BaseModel):
    """Response body for video search"""
    query: str
    recommendations: List[VideoResponse]


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "youtube-recommender"}


@app.post("/api/search", response_model=SearchResponse)
async def search_videos(request: SearchRequest):
    """Search for videos and return recommendations.

    This endpoint:
    1. Builds search query from structured parameters
    2. Searches YouTube for videos matching the query
    3. Retrieves detailed statistics for each video
    4. Scores videos based on relevance, quality, recency, etc.
    5. Returns top 3 recommended videos
    """
    yt_service = get_youtube_service()
    rec_engine = get_recommender()

    # Build query from structured parameters
    query = request.build_query()

    # Get published after date from max_months
    published_after = YouTubeService.get_published_after_from_months(request.max_months)

    try:
        # Search and get video details
        videos = yt_service.search_and_get_details(
            query=query,
            max_results=rec_engine.filters["default_max_results"],
            published_after=published_after,
            video_duration=None,  # Filter in recommender for more precision
        )

        if not videos:
            return SearchResponse(query=query, recommendations=[])

        # Rank videos and get recommendations
        recommendations = rec_engine.rank_videos(
            videos=videos,
            duration_preference=request.duration_preference,
        )

        # Convert to response format
        response_recommendations = []
        for rec in recommendations:
            breakdown = ScoreBreakdownResponse(
                relevance=round(rec.score_breakdown.relevance, 4),
                like_ratio=round(rec.score_breakdown.like_ratio, 4),
                views=round(rec.score_breakdown.views, 4),
                recency=round(rec.score_breakdown.recency, 4),
                duration_match=round(rec.score_breakdown.duration_match, 4),
            )
            response_recommendations.append(
                VideoResponse(
                    video_id=rec.video_id,
                    title=rec.title,
                    channel=rec.channel,
                    thumbnail=rec.thumbnail,
                    duration=rec.duration,
                    duration_seconds=rec.duration_seconds,
                    view_count=rec.view_count,
                    like_count=rec.like_count,
                    published_at=rec.published_at,
                    score=rec.score,
                    score_breakdown=breakdown,
                )
            )

        return SearchResponse(
            query=query,
            recommendations=response_recommendations,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
