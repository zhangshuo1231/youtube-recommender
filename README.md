# YouTube Tutorial Recommender

A web application that searches YouTube and recommends the best video tutorials based on quality metrics including relevance, engagement, recency, and duration preferences.

## Deployment Status

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel | https://youtube-recommender-theta.vercel.app |
| Backend | Railway | (check Railway dashboard for current URL) |
| Repository | GitHub | https://github.com/zhangshuo1231/youtube-recommender |

### Environment Variables

**Backend (Railway):**
- `YOUTUBE_API_KEY` - YouTube Data API v3 key (required)
- `PORT` - Auto-injected by Railway

**Frontend (Vercel):**
- `NEXT_PUBLIC_API_URL` - Backend URL with `https://` prefix, no trailing slash

---

## Features

- Structured input form: technology name, skill level, duration preference, time filter
- Smart recommendation algorithm with configurable weights
- Returns top 3 recommended videos with detailed score breakdown
- Clean, modern UI design (blue-green gradient theme)

---

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+
- **API**: YouTube Data API v3
- **Deployment**: Vercel (frontend) + Railway (backend)

---

## Project Structure

```
youtube-recommender/
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── page.tsx            # Main page with search form
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Global styles (blue-green theme)
│   ├── components/
│   │   └── VideoCard.tsx       # Video recommendation card component
│   ├── lib/
│   │   └── api.ts              # Backend API client
│   ├── package.json
│   └── .env.local.example
│
├── backend/
│   ├── main.py                 # FastAPI entry point, /api/search endpoint
│   ├── youtube_service.py      # YouTube Data API wrapper
│   ├── recommender.py          # Scoring algorithm implementation
│   ├── config.yaml             # Scoring weights configuration
│   ├── analyzers/              # Future: LLM comment analysis module
│   │   ├── __init__.py
│   │   └── base.py             # Analyzer interface
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── railway.json            # Railway deployment config
│   └── .env.example
│
└── README.md                   # This file
```

---

## Recommendation Algorithm

### Scoring Weights (configurable in `backend/config.yaml`)

| Factor | Weight | Description |
|--------|--------|-------------|
| Relevance | 30% | YouTube search result ranking position |
| Like Ratio | 25% | views/likes ratio (lower = better quality) |
| View Count | 20% | Logarithmic normalization of total views |
| Recency | 15% | How recently the video was uploaded |
| Duration Match | 10% | Match with user's duration preference |

### Duration Preferences

| Option | Range |
|--------|-------|
| short | < 10 minutes |
| medium | 10-30 minutes |
| long | > 30 minutes |
| any | No filter |

### Skill Level

Appended to search query as keywords:
- beginner → "tutorial for beginners"
- intermediate → "intermediate tutorial"
- advanced → "advanced tutorial"

---

## API Reference

### Health Check
```
GET /health
Response: { "status": "healthy" }
```

### Search Videos
```
POST /api/search
Content-Type: application/json

Request Body:
{
  "technology": "React",                    // Required
  "level": "beginner",                      // Optional: beginner/intermediate/advanced
  "duration_preference": "medium",          // Optional: short/medium/long/any (default: any)
  "max_months": 12                          // Optional: filter videos within N months
}

Response:
{
  "query": "React tutorial for beginners",
  "recommendations": [
    {
      "video_id": "xxx",
      "title": "...",
      "channel": "...",
      "thumbnail": "https://...",
      "duration": "15:30",
      "duration_seconds": 930,
      "view_count": 100000,
      "like_count": 5000,
      "published_at": "2024-01-15T...",
      "score": 0.85,
      "score_breakdown": {
        "relevance": 0.30,
        "like_ratio": 0.22,
        "views": 0.18,
        "recency": 0.10,
        "duration_match": 0.05
      }
    }
  ]
}
```

---

## Local Development

### Prerequisites

1. Python 3.11+
2. Node.js 18+
3. YouTube Data API key ([Get one here](https://console.cloud.google.com/))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env: YOUTUBE_API_KEY=your_key_here

# Run server
uvicorn main:app --reload
# Or: python main.py
```

Backend: http://localhost:8000

### Frontend Setup

```bash
cd frontend

npm install

# Configure environment (optional for local dev)
cp .env.local.example .env.local
# Default API_URL points to localhost:8000

npm run dev
```

Frontend: http://localhost:3000

---

## Deployment Guide

### Backend → Railway

1. Create new project on Railway
2. Connect GitHub repo: `zhangshuo1231/youtube-recommender`
3. **Set Root Directory**: `backend` (in Settings → General)
4. Add Environment Variable: `YOUTUBE_API_KEY`
5. Railway auto-detects Dockerfile and deploys
6. Copy the generated public URL (Settings → Networking → Public Networking)

**Important files for Railway:**
- `backend/Dockerfile` - Build configuration
- `backend/railway.json` - Deployment settings (uses DOCKERFILE builder, no startCommand)

### Frontend → Vercel

1. Import project from GitHub
2. **Set Root Directory**: `frontend`
3. Add Environment Variable: `NEXT_PUBLIC_API_URL` = Railway backend URL
   - Must include `https://` prefix
   - Must NOT have trailing slash
4. Deploy

---

## Architecture Notes

### Future Extension: LLM Comment Analysis

The `backend/analyzers/` module is prepared for future LLM-based comment analysis:

```python
# backend/analyzers/base.py defines the interface:
class BaseAnalyzer:
    async def analyze(self, video_id: str, comments: List[str]) -> AnalysisResult
```

To enable:
1. Add LLM API key to environment
2. Set `comment_analysis.enabled: true` in config.yaml
3. Implement analyzer in `backend/analyzers/comment_analyzer.py`

Purpose: Detect marketing content, outdated information, hidden promotional agendas.

### Design Decisions

1. **FastAPI over Flask**: Better async support, automatic OpenAPI docs, type hints
2. **Next.js over plain React**: Easier Vercel deployment, better SEO potential
3. **Structured input over free text**: More predictable search results, better UX
4. **Configurable weights in YAML**: Easy tuning without code changes
5. **Like ratio = views/likes**: Lower ratio means higher engagement quality

---

## Troubleshooting

### Common Issues

**405 Method Not Allowed on API calls:**
- Check `NEXT_PUBLIC_API_URL` in Vercel has correct format
- Must be: `https://xxx.up.railway.app` (with https, no trailing slash)
- Redeploy frontend after changing env vars

**Railway deployment fails with "Error creating build plan":**
- Ensure Root Directory is set to `backend`
- Check `railway.json` exists and uses DOCKERFILE builder

**"$PORT is not a valid integer" error:**
- Remove `startCommand` from `railway.json`
- Use `CMD ["python", "main.py"]` in Dockerfile (reads PORT via os.getenv)

**YouTube API quota exceeded:**
- Free tier: 10,000 units/day
- Each search costs ~100 units
- Consider caching or rate limiting

---

## License

MIT
