'use client';

import { useState } from 'react';
import { searchVideos, VideoRecommendation } from '@/lib/api';

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
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 7) {
    return `${diffDays} days ago`;
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    return `${months} month${months > 1 ? 's' : ''} ago`;
  } else {
    const years = Math.floor(diffDays / 365);
    return `${years} year${years > 1 ? 's' : ''} ago`;
  }
}

export default function Home() {
  const [technology, setTechnology] = useState('');
  const [level, setLevel] = useState<'beginner' | 'intermediate' | 'advanced' | ''>('');
  const [duration, setDuration] = useState<'short' | 'medium' | 'long' | 'any'>('any');
  const [maxMonths, setMaxMonths] = useState<string>('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<VideoRecommendation[]>([]);
  const [searchedQuery, setSearchedQuery] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!technology.trim()) {
      setError('Please enter a technology name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await searchVideos({
        technology: technology.trim(),
        level: level || null,
        duration_preference: duration,
        max_months: maxMonths ? parseInt(maxMonths) : null,
      });

      setResults(response.recommendations);
      setSearchedQuery(response.query);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="main-container">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">▶</div>
          <h1 className="title">TutorialFinder</h1>
        </div>
        <p className="subtitle">Discover the best video tutorials for your learning journey</p>
      </header>

      <div className="search-card">
        <form onSubmit={handleSearch} className="search-form">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">
                Technology <span className="required">*</span>
              </label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., React, Python, Docker, Kubernetes..."
                value={technology}
                onChange={(e) => setTechnology(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Skill Level</label>
              <select
                className="form-select"
                value={level}
                onChange={(e) => setLevel(e.target.value as typeof level)}
              >
                <option value="">Any level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>

          <div className="filters-row">
            <div className="form-group">
              <label className="form-label">Video Duration</label>
              <select
                className="form-select"
                value={duration}
                onChange={(e) => setDuration(e.target.value as typeof duration)}
              >
                <option value="any">Any length</option>
                <option value="short">Short (&lt; 10 min)</option>
                <option value="medium">Medium (10-30 min)</option>
                <option value="long">Long (&gt; 30 min)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Upload Time</label>
              <select
                className="form-select"
                value={maxMonths}
                onChange={(e) => setMaxMonths(e.target.value)}
              >
                <option value="">Any time</option>
                <option value="1">Past month</option>
                <option value="3">Past 3 months</option>
                <option value="6">Past 6 months</option>
                <option value="12">Past year</option>
                <option value="24">Past 2 years</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">&nbsp;</label>
              <button type="submit" className="search-button" disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
                    Searching...
                  </>
                ) : (
                  'Find Tutorials'
                )}
              </button>
            </div>
          </div>
        </form>
      </div>

      {error && (
        <div className="error-message">
          <span>⚠️</span>
          {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <p>Searching for the best tutorials...</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <section className="results-section">
          <div className="results-header">
            <div className="results-icon">✓</div>
            <h2 className="results-title">
              Top 3 Recommendations <span className="results-query">for "{searchedQuery}"</span>
            </h2>
          </div>

          <div className="results-grid">
            {results.map((video, index) => (
              <article key={video.video_id} className="video-card">
                <div className="rank-badge">#{index + 1}</div>

                <div className="thumbnail-container">
                  <a
                    href={`https://www.youtube.com/watch?v=${video.video_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="thumbnail-link"
                  >
                    <img
                      src={video.thumbnail}
                      alt={video.title}
                      className="thumbnail"
                    />
                    <span className="duration-badge">{video.duration}</span>
                  </a>
                </div>

                <div className="video-info">
                  <a
                    href={`https://www.youtube.com/watch?v=${video.video_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="video-title"
                  >
                    {video.title}
                  </a>

                  <div className="channel-name">{video.channel}</div>

                  <div className="video-stats">
                    <span className="stat-item">
                      {formatNumber(video.view_count)} views
                    </span>
                    <span className="stat-item">
                      {formatNumber(video.like_count)} likes
                    </span>
                    <span className="stat-item">
                      {formatDate(video.published_at)}
                    </span>
                  </div>

                  <div className="score-section">
                    <div className="score-header">
                      <span className="score-label">Recommendation Score</span>
                      <span className="score-value">{Math.round(video.score * 100)}%</span>
                    </div>
                    <div className="score-bar">
                      <div
                        className="score-fill"
                        style={{ width: `${video.score * 100}%` }}
                      />
                    </div>
                    <div className="score-breakdown">
                      <div className="breakdown-item">
                        <span className="breakdown-label">Relevance</span>
                        <span className="breakdown-value">
                          {Math.round(video.score_breakdown.relevance * 100)}%
                        </span>
                      </div>
                      <div className="breakdown-item">
                        <span className="breakdown-label">Like Ratio</span>
                        <span className="breakdown-value">
                          {Math.round(video.score_breakdown.like_ratio * 100)}%
                        </span>
                      </div>
                      <div className="breakdown-item">
                        <span className="breakdown-label">Views</span>
                        <span className="breakdown-value">
                          {Math.round(video.score_breakdown.views * 100)}%
                        </span>
                      </div>
                      <div className="breakdown-item">
                        <span className="breakdown-label">Recency</span>
                        <span className="breakdown-value">
                          {Math.round(video.score_breakdown.recency * 100)}%
                        </span>
                      </div>
                      <div className="breakdown-item">
                        <span className="breakdown-label">Duration</span>
                        <span className="breakdown-value">
                          {Math.round(video.score_breakdown.duration_match * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      {!loading && results.length === 0 && searchedQuery && (
        <div className="no-results">
          <div className="no-results-icon">🔍</div>
          <p>No tutorials found for "{searchedQuery}"</p>
          <p>Try a different technology or adjust your filters</p>
        </div>
      )}
    </main>
  );
}
