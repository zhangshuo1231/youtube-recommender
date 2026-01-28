# YouTube Tutorial Recommender

A web application that searches YouTube and recommends the best video tutorials based on quality metrics including relevance, engagement, recency, and duration preferences.

## Features

- Search YouTube for video tutorials
- Smart recommendation algorithm considering:
  - Search relevance (30%)
  - Like-to-view ratio (25%)
  - View count with logarithmic normalization (20%)
  - Video recency (15%)
  - Duration preference matching (10%)
- Filter by video duration (short/medium/long)
- Filter by upload date (week/month/year)
- Returns top 3 recommended videos with score breakdown

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, React
- **Backend**: FastAPI, Python 3.11+
- **API**: YouTube Data API v3

## Project Structure

```
youtube-recommender/
├── frontend/           # Next.js application
│   ├── app/           # App Router pages
│   ├── components/    # React components
│   └── lib/           # API utilities
│
├── backend/           # FastAPI application
│   ├── analyzers/     # Extensible analyzer modules
│   ├── main.py        # API entry point
│   ├── youtube_service.py
│   ├── recommender.py
│   └── config.yaml    # Scoring weights configuration
│
└── README.md
```

## Setup

### Prerequisites

1. Python 3.11+
2. Node.js 18+
3. YouTube Data API key ([Get one here](https://console.cloud.google.com/))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your YOUTUBE_API_KEY

# Run the server
uvicorn main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local if needed (default points to localhost:8000)

# Run the development server
npm run dev
```

Frontend will be available at http://localhost:3000

## API Endpoints

### Health Check
```
GET /health
```

### Search Videos
```
POST /api/search
Content-Type: application/json

{
  "query": "Python tutorial for beginners",
  "duration_preference": "medium",  // short/medium/long/any
  "upload_date": "any"              // week/month/year/any
}
```

## Configuration

Scoring weights can be adjusted in `backend/config.yaml`:

```yaml
scoring:
  relevance_weight: 0.30
  like_ratio_weight: 0.25
  view_count_weight: 0.20
  recency_weight: 0.15
  duration_match_weight: 0.10
```

## Deployment

### Backend (Railway/Render)

1. Connect your GitHub repository
2. Set root directory to `backend`
3. Add environment variable: `YOUTUBE_API_KEY`
4. Deploy automatically

### Frontend (Vercel)

1. Connect your GitHub repository
2. Set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL` (your backend URL)
4. Deploy automatically

## Future Enhancements

The architecture supports future additions:

- **Comment Analysis Module**: LLM-based analysis of video comments to detect:
  - Marketing/clickbait content
  - Outdated information
  - Promotional content with hidden agendas

Enable by setting `comment_analysis.enabled: true` in `config.yaml` (requires LLM API key).

## License

MIT
