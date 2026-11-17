
import os
import json
import time

from pydantic import ValidationError
from validate_tmdb import MovieReview

from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from supabase import create_client


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TMDB_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not all([TMDB_TOKEN, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing API credentials in .env")


HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json"
}

# Reuse connections for multiple TMDB requests
session = requests.Session()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)




def fetch_tmdb(endpoint, params=None):
    """Fetch TMDB data with retries for temporary errors."""

    url = f"https://api.themoviedb.org/3/{endpoint}"

    max_attempts = 4

    for attempt in range(max_attempts):
        try:
            response = session.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=(10, 30)
            )

            
            # Check for HTTP errors
            response.raise_for_status()

            time.sleep(0.3)
            return response.json()

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError
        ) as error:

            # Do not retry permanent HTTP errors
            if (
                isinstance(error, requests.exceptions.HTTPError)
                and error.response is not None
                and error.response.status_code
                not in [429, 500, 502, 503, 504]
            ):
                raise

            if attempt == max_attempts - 1:
                print("TMDB request failed after retries.")
                raise

            wait = 2 ** (attempt + 1)

            print(
                f"Temporary API error. "
                f"Retrying in {wait} seconds..."
            )

            time.sleep(wait)

    


def get_movies():
    """Select a variety of movies."""

    trending = fetch_tmdb("trending/movie/day")

    movies = trending.get("results", [])[:10]

    # Include lower-rated movies
    for page in range(1, 4):
        result = fetch_tmdb(
            "discover/movie",
            {
                "sort_by": "popularity.desc",
                "vote_average.lte": 5,
                "vote_count.gte": 100,
                "page": page
            }
        )
        movies.extend(result.get("results", []))

    # Include popular movies
    popular = fetch_tmdb("movie/popular")
    movies.extend(popular.get("results", []))

    # Remove duplicate movie IDs
    unique_movies = {
        movie["id"]: movie
        for movie in movies
    }

    return list(unique_movies.values())


def get_sentiment(rating):
    """Create approximate labels from reviewer ratings."""

    if rating is None:
        return None

    if rating >= 7:
        return "Positive"

    if rating <= 4:
        return "Negative"

    return "Neutral"


def main():
    print("Starting live TMDB collection...")

    movies = get_movies()
    now = datetime.now(timezone.utc).isoformat()

    raw_reviews = []
    records = {}
    invalid_reviews = 0
    skipped_movies = 0

    for movie in movies:
        movie_id = movie["id"]
        title = movie["title"]

        
        try:
            first_page = fetch_tmdb(
                f"movie/{movie_id}/reviews"
            )

            all_reviews = first_page.get("results", [])

            total_pages = min(
                first_page.get("total_pages", 1),
                3
            )

            for page in range(2, total_pages + 1):
                next_page = fetch_tmdb(
                    f"movie/{movie_id}/reviews",
                    {"page": page}
                )
                all_reviews.extend(
                    next_page.get("results", [])
                )

        except requests.exceptions.RequestException as error:

            # Stop for permanent HTTP errors
            if (
                isinstance(error, requests.exceptions.HTTPError)
                and error.response is not None
                and error.response.status_code
                not in [429, 500, 502, 503, 504]
            ):
                raise

            print(
                f"Skipping {title}: "
                f"TMDB request failed after retries: {error}"
            )

            skipped_movies += 1  # YAHAN ADD KARNA HAI
            continue

            # Stop for permanent HTTP errors
            if (
                isinstance(error, requests.exceptions.HTTPError)
                and error.response is not None
                and error.response.status_code
                not in [429, 500, 502, 503, 504]
            ):
                raise

            print(
                f"Skipping {title}: "
                f"TMDB request failed after retries: {error}"
            )
            continue


        
        for review in all_reviews:

            # Validate review using Pydantic
            try:
                validated = MovieReview.model_validate({
                    "movie_id": movie_id,
                    "movie_title": title,
                    "review": review
                })

            except ValidationError:
                invalid_reviews += 1
                continue

            # Use cleaned and validated values
            review_id = validated.review.id
            content = validated.review.content
            rating = validated.review.author_details.rating


            raw_reviews.append({
                "movie_id": movie_id,
                "movie_title": title,
                "review": review
            })

            records[review_id] = {
                "review_id": review_id,
                "movie_id": movie_id,
                "movie_title": title,
                "author": review.get("author"),
                "review_text": content,
                "rating": rating,
                "sentiment_label": get_sentiment(rating),
                "label_source": (
                    "rating_derived" if rating is not None else None
                ),
                "review_created_at": review.get("created_at"),
                "review_updated_at": review.get("updated_at"),
                "last_seen_at": now,
                "raw_json": review
            }

        print(f"{title}: {len(all_reviews)} reviews checked")
    
    # Stop if no movies were available
    if not movies:
        raise RuntimeError("TMDB returned no movies.")

    # Stop if every movie request failed
    if skipped_movies == len(movies):
        raise RuntimeError(
            "Collection failed: all movie requests were skipped."
        )

    # Save a JSON snapshot of this collection
    output_dir = BASE_DIR / "data" / "tmdb_captures"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    output_file = output_dir / f"capture_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            {
                "captured_at": now,
                "source": "TMDB",
                "movies_checked": len(movies),
                "reviews": raw_reviews
            },
            file,
            indent=2,
            ensure_ascii=False
        )
    
    # Save movie statistics history to Supabase
    movie_history = []

    for movie in movies:
        movie_history.append({
            "movie_id": movie["id"],
            "movie_title": movie.get("title") or "Unknown Movie",
            "popularity": movie.get("popularity"),
            "vote_average": movie.get("vote_average"),
            "vote_count": movie.get("vote_count"),
            "captured_at": now,
            "raw_json": movie
        })

    # Upload movie snapshots in batches
    for start in range(0, len(movie_history), 50):
        batch = movie_history[start:start + 50]

        supabase.table("tmdb_movie_history").insert(
            batch
        ).execute()

    print(f"Movie history snapshots saved: {len(movie_history)}")

    # Save new and existing reviews to Supabase
    rows = list(records.values())
    new_count = 0

    for start in range(0, len(rows), 50):
        batch = rows[start:start + 50]
        ids = [row["review_id"] for row in batch]

        result = (
            supabase.table("tmdb_reviews")
            .select("review_id, first_seen_at")
            .in_("review_id", ids)
            .execute()
        )

        existing = {
            row["review_id"]: row["first_seen_at"]
            for row in result.data
        }

        for row in batch:
            if row["review_id"] not in existing:
                new_count += 1

            row["first_seen_at"] = existing.get(
                row["review_id"], now
            )

        supabase.table("tmdb_reviews").upsert(
            batch,
            on_conflict="review_id"
        ).execute()

    print("\n--- LIVE COLLECTION REPORT ---")
    print(f"Movies successfully processed: {len(movies) - skipped_movies}")
    print(f"Movies skipped: {skipped_movies}")
    print(f"Unique reviews checked: {len(rows)}")
    print(f"Invalid reviews rejected: {invalid_reviews}")
    print(f"New reviews inserted: {new_count}")
    print(f"Existing reviews rechecked: {len(rows) - new_count}")
    print(f"JSON saved: {output_file}")
    print("\nLive collection completed!")


if __name__ == "__main__":
    main()
