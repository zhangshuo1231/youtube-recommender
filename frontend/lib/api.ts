const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ScoreBreakdown {
  relevance: number;
  like_ratio: number;
  views: number;
  recency: number;
  duration_match: number;
}

export interface VideoRecommendation {
  video_id: string;
  title: string;
  channel: string;
  thumbnail: string;
  duration: string;
  duration_seconds: number;
  view_count: number;
  like_count: number;
  published_at: string;
  score: number;
  score_breakdown: ScoreBreakdown;
}

export interface SearchResponse {
  query: string;
  recommendations: VideoRecommendation[];
}

export interface SearchParams {
  technology: string;
  level?: 'beginner' | 'intermediate' | 'advanced' | null;
  duration_preference?: 'short' | 'medium' | 'long' | 'any';
  max_months?: number | null;
}

export async function searchVideos(params: SearchParams): Promise<SearchResponse> {
  const body: Record<string, unknown> = {
    technology: params.technology,
    duration_preference: params.duration_preference || 'any',
  };

  if (params.level) {
    body.level = params.level;
  }

  if (params.max_months) {
    body.max_months = params.max_months;
  }

  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
