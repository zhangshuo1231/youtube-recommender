'use client';

import { VideoRecommendation } from '@/lib/api';

interface VideoCardProps {
  video: VideoRecommendation;
  rank: number;
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays < 7) {
    return `${diffDays} days ago`;
  } else if (diffDays < 30) {
    return `${Math.floor(diffDays / 7)} weeks ago`;
  } else if (diffDays < 365) {
    return `${Math.floor(diffDays / 30)} months ago`;
  } else {
    return `${Math.floor(diffDays / 365)} years ago`;
  }
}

export default function VideoCard({ video, rank }: VideoCardProps) {
  const videoUrl = `https://www.youtube.com/watch?v=${video.video_id}`;
  const scorePercent = Math.round(video.score * 100);

  return (
    <div className="video-card">
      <div className="rank-badge">#{rank}</div>

      <a href={videoUrl} target="_blank" rel="noopener noreferrer" className="thumbnail-link">
        <img
          src={video.thumbnail}
          alt={video.title}
          className="thumbnail"
        />
        <span className="duration-badge">{video.duration}</span>
      </a>

      <div className="video-info">
        <a href={videoUrl} target="_blank" rel="noopener noreferrer" className="video-title">
          {video.title}
        </a>

        <div className="channel-name">{video.channel}</div>

        <div className="video-stats">
          <span>{formatNumber(video.view_count)} views</span>
          <span className="dot">·</span>
          <span>{formatNumber(video.like_count)} likes</span>
          <span className="dot">·</span>
          <span>{formatDate(video.published_at)}</span>
        </div>

        <div className="score-section">
          <div className="score-header">
            <span className="score-label">Recommendation Score</span>
            <span className="score-value">{scorePercent}%</span>
          </div>
          <div className="score-bar">
            <div className="score-fill" style={{ width: `${scorePercent}%` }} />
          </div>

          <div className="score-breakdown">
            <div className="breakdown-item">
              <span className="breakdown-label">Relevance</span>
              <span className="breakdown-value">{(video.score_breakdown.relevance * 100).toFixed(1)}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Like Ratio</span>
              <span className="breakdown-value">{(video.score_breakdown.like_ratio * 100).toFixed(1)}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Views</span>
              <span className="breakdown-value">{(video.score_breakdown.views * 100).toFixed(1)}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Recency</span>
              <span className="breakdown-value">{(video.score_breakdown.recency * 100).toFixed(1)}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Duration</span>
              <span className="breakdown-value">{(video.score_breakdown.duration_match * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
