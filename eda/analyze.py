
import os
import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from dotenv import load_dotenv
from supabase import create_client


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "eda" / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

sns.set_theme(style="whitegrid")


def load_reviews():
    """Read all TMDB reviews from Supabase."""

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise ValueError("Missing Supabase credentials.")

    client = create_client(url, key)

    records = []
    start = 0

    while True:
        response = (
            client.table("tmdb_reviews")
            .select(
                "review_id,movie_title,review_text,"
                "rating,sentiment_label,first_seen_at"
            )
            .order("review_id")
            .range(start, start + 999)
            .execute()
        )

        batch = response.data or []
        records.extend(batch)

        if len(batch) < 1000:
            break

        start += 1000

    return pd.DataFrame(records)


def save_graph(filename):
    """Save the current graph as PNG."""

    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR / filename,
        dpi=160,
        bbox_inches="tight"
    )
    plt.close()


def main():
    print("Starting TMDB Exploratory Data Analysis...")

    df = load_reviews()

    if df.empty:
        print("No reviews found in Supabase.")
        return

    # Prepare the data
    df["review_text"] = (
        df["review_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["movie_title"] = (
        df["movie_title"]
        .fillna("Unknown Movie")
    )

    df["sentiment_label"] = (
        df["sentiment_label"]
        .fillna("Unlabeled")
        .replace("", "Unlabeled")
    )

    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

    df["word_count"] = (
        df["review_text"]
        .str.split()
        .str.len()
    )

    df["first_seen_at"] = pd.to_datetime(
        df["first_seen_at"],
        errors="coerce",
        utc=True
    )

    # Basic statistics
    total_reviews = len(df)
    total_movies = df["movie_title"].nunique()

    sentiment_counts = (
        df["sentiment_label"]
        .value_counts()
        .reindex(
            ["Positive", "Negative", "Neutral", "Unlabeled"],
            fill_value=0
        )
    )

    ratings = df["rating"].dropna()

    # Graph 1: Sentiment Distribution
    plt.figure(figsize=(8, 5))

    plt.bar(
        sentiment_counts.index,
        sentiment_counts.values
    )

    plt.title("TMDB Review Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Number of Reviews")

    save_graph("01_sentiment_distribution.png")

    
    # Graph 2: Reviewer Rating Distribution
    plt.figure(figsize=(8, 5))

    if not ratings.empty:
        plt.hist(
            ratings,
            bins=20,
            edgecolor="white"
        )
    else:
        plt.text(
            0.5, 0.5,
            "No rated reviews available",
            ha="center",
            va="center",
            transform=plt.gca().transAxes
        )

    plt.title("Reviewer Rating Distribution")
    plt.xlabel("Rating (0-10)")
    plt.ylabel("Number of Reviews")
    plt.xlim(0, 10)

    save_graph("02_rating_distribution.png")


    # Graph 3: Top Reviewed Movies
    top_movies = (
        df["movie_title"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        top_movies.index,
        top_movies.values
    )

    plt.title("Top 10 Movies by Review Count")
    plt.xlabel("Number of Reviews")

    save_graph("03_top_movies.png")

    # Graph 4: Review Length Distribution
    plt.figure(figsize=(8, 5))

    plt.hist(
        df["word_count"],
        bins=20,
        edgecolor="white"
    )

    plt.title("Review Length Distribution")
    plt.xlabel("Number of Words")
    plt.ylabel("Number of Reviews")

    save_graph("04_review_lengths.png")

    # Graph 5 and 6: Collection History
    collection_dates = df["first_seen_at"].dropna()

    if not collection_dates.empty:
        daily_counts = (
            collection_dates.dt.floor("D")
            .value_counts()
            .sort_index()
            .asfreq("D", fill_value=0)
        )

        # Daily collection graph
        plt.figure(figsize=(9, 5))

        plt.bar(
            daily_counts.index,
            daily_counts.values,
            width=0.7
        )

        plt.title("New Reviews Collected Per Day")
        plt.xlabel("Collection Date (UTC)")
        plt.ylabel("New Reviews")
        plt.xticks(rotation=30)

        save_graph("05_daily_collection.png")

        # Cumulative collection graph
        cumulative = daily_counts.cumsum()

        plt.figure(figsize=(9, 5))

        plt.plot(
            cumulative.index,
            cumulative.values,
            marker="o"
        )

        plt.title("Total Reviews Collected Over Time")
        plt.xlabel("Collection Date (UTC)")
        plt.ylabel("Total Collected Reviews")
        plt.xticks(rotation=30)

        save_graph("06_cumulative_collection.png")

    # Data quality statistics
    empty_reviews = int(
        df["review_text"].eq("").sum()
    )

    duplicate_ids = int(
        df["review_id"].duplicated().sum()
    )

    missing_ratings = int(
        df["rating"].isna().sum()
    )

    # Create EDA summary
    report = {
        "source": "TMDB API via Supabase",
        "analyzed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_reviews": total_reviews,
        "total_movies": total_movies,
        "sentiment_distribution": {
            label: int(count)
            for label, count in sentiment_counts.items()
        },
        "rated_reviews": int(len(ratings)),
        "missing_ratings": missing_ratings,
        "average_rating": (
            round(float(ratings.mean()), 2)
            if not ratings.empty else None
        ),
        "average_word_count": round(
            float(df["word_count"].mean()), 2
        ),
        "median_word_count": float(
            df["word_count"].median()
        ),
        "empty_reviews": empty_reviews,
        "duplicate_review_ids": duplicate_ids,
        "top_reviewed_movies": {
            title: int(count)
            for title, count in top_movies.sort_values(
                ascending=False
            ).items()
        }
    }

    # Save report as JSON
    json_path = RESULTS_DIR / "eda_summary.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Save readable text report
    text_path = RESULTS_DIR / "eda_report.txt"

    with open(text_path, "w", encoding="utf-8") as file:
        file.write("TMDB EXPLORATORY DATA ANALYSIS REPORT\n")
        file.write("=" * 42 + "\n\n")

        for key, value in report.items():
            file.write(f"{key}: {value}\n")

        file.write("\nINTERPRETATION\n")
        file.write(
            "Sentiment labels are approximate and "
            "derived from reviewer ratings.\n"
        )
        file.write(
            "Collection trends show when our system "
            "first discovered reviews, not when "
            "reviews were published.\n"
        )
        file.write(
            "Results describe the reviews currently "
            "stored in Supabase.\n"
        )

    print("\n--- EDA REPORT ---")
    print(f"Total Reviews: {total_reviews}")
    print(f"Total Movies: {total_movies}")
    print(f"Rated Reviews: {len(ratings)}")
    print(f"Missing Ratings: {missing_ratings}")
    print(f"Empty Reviews: {empty_reviews}")
    print(f"Duplicate IDs: {duplicate_ids}")

    print("\nSentiment Distribution:")
    print(sentiment_counts.to_string())

    print("\nEDA completed successfully!")
    print(f"Graphs and reports saved in: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
