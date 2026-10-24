
from pathlib import Path
import os
import httpx
from dotenv import load_dotenv
import joblib
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
MODEL_DIR = BASE_DIR / "model"

# Load saved Colab artifacts
df = joblib.load(MODEL_DIR / "df.pkl")
indices = joblib.load(MODEL_DIR / "indices.pkl")
tf_idf = joblib.load(MODEL_DIR / "tf_idf.pkl")
tfidf_matrix = joblib.load(MODEL_DIR / "tfidf_matrix.pkl")

app = FastAPI(title="Movie Recommendation System API")

# Allow our future React frontend to connect
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://moviere-commendation-bclk.vercel.app",
        "https://moviere-commendation-git-main-hyuk14.vercel.app",
        "https://moviere-commendation-btiv8hrp6-hyuk14.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Movie Recommendation API is running"}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "total_movies": len(df),
        "model_loaded": tfidf_matrix is not None
    }


@app.get("/api/movies")
def search_movies(q: str = Query(..., min_length=1)):
    if "Title" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail=f"Title column not found. Available columns: {list(df.columns)}"
        )

    titles = df["Title"].fillna("").astype(str).str.strip()

    matches = df.loc[
        titles.str.contains(q, case=False, regex=False)
    ].head(10)

    return {
    "results": titles[
        titles.str.contains(q.strip(), case=False, regex=False)
    ].head(10).tolist()
}


async def get_tmdb_details(client: httpx.AsyncClient, title: str):
    """Find a movie on TMDB and return its display information."""

    if not TMDB_API_KEY:
        return None

    url = f"{TMDB_BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "include_adult": False,
    }

    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return None

        # Prefer an exact title match over a loosely matching result
        matched = next(
            (
                movie for movie in results
                if movie.get("title", "").strip().casefold()
                == title.strip().casefold()
            ),
            results[0],
        )

        poster_path = matched.get("poster_path")

        return {
            "tmdb_id": matched.get("id"),
            "poster_url": (
                f"https://image.tmdb.org/t/p/w500{poster_path}"
                if poster_path else None
            ),
            "rating": matched.get("vote_average"),
            "overview": matched.get("overview") or None,
            "release_date": matched.get("release_date") or None,
        }

    except (httpx.HTTPError, ValueError):
        # Recommendations should still work if TMDB is unavailable
        return None


@app.get("/api/recommendations")
async def recommend_movies(
    title: str,
    limit: int = Query(8, ge=1, le=20),
):
    titles = df["Title"].fillna("").astype(str).str.strip()

    title_to_index = {
        movie_title.casefold(): row_index
        for row_index, movie_title in enumerate(titles)
    }

    movie_index = title_to_index.get(title.strip().casefold())

    if movie_index is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found. Search for a valid title first.",
        )

    # Existing TF-IDF recommendation algorithm
    similarity_scores = cosine_similarity(
        tfidf_matrix[movie_index],
        tfidf_matrix,
    ).flatten()

    ranked_indices = similarity_scores.argsort()[::-1]
    ranked_indices = [
        i for i in ranked_indices if i != movie_index
    ][:limit]

    # Fetch TMDB information for each recommended movie
    async with httpx.AsyncClient(timeout=15.0) as client:
        recommendations = []

        for i in ranked_indices:
            movie_title = titles.iloc[i]

            tmdb_details = await get_tmdb_details(
                client, movie_title
            )

            recommendations.append({
                "title": movie_title,
                "similarity": round(
                    float(similarity_scores[i]), 4
                ),
                "poster_url": (
                    tmdb_details["poster_url"]
                    if tmdb_details else None
                ),
                "rating": (
                    tmdb_details["rating"]
                    if tmdb_details else None
                ),
                "overview": (
                    tmdb_details["overview"]
                    if tmdb_details else None
                ),
                "release_date": (
                    tmdb_details["release_date"]
                    if tmdb_details else None
                ),
                "tmdb_id": (
                    tmdb_details["tmdb_id"]
                    if tmdb_details else None
                ),
            })

    return {
        "selected_movie": titles.iloc[movie_index],
        "recommendations": recommendations,
    }


@app.get("/api/tmdb/search")
async def tmdb_search(q: str = Query(..., min_length=1)):
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="TMDB_API_KEY is missing from the root .env file"
        )

    url = f"{TMDB_BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": q.strip(),
        "include_adult": False,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB returned HTTP {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to TMDB"
        ) from exc

    results = []

    for movie in data.get("results", [])[:10]:
        poster_path = movie.get("poster_path")

        results.append({
            "tmdb_id": movie.get("id"),
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "rating": movie.get("vote_average"),
            "overview": movie.get("overview"),
            "poster_url": (
                f"https://image.tmdb.org/t/p/w500{poster_path}"
                if poster_path else None
            ),
        })

    return {"results": results}
