LIVE MOVIE REVIEW SENTIMENT ANALYTICS (MOVIE PULSE)
===================================================
UNIVERSITY PROJECT 1 - ETL + EXPLORATORY DATA ANALYSIS (EDA)

PUBLIC DASHBOARD
----------------
https://movie-pulse-analytics.streamlit.app/

GITHUB REPOSITORY
-----------------
https://github.com/umerirfan6528-commits/Movie-Sentiment-Analysis

1. PROJECT OVERVIEW
-------------------
Movie Pulse is a Python-based ETL and EDA project that collects and analyzes
movie reviews and movie statistics from the TMDB (The Movie Database) API.

The system extracts selected TMDB reviews, validates them with Pydantic,
saves JSON snapshots, and stores review records and movie-history snapshots
in Supabase PostgreSQL. It also produces EDA reports and provides an
interactive, publicly accessible Streamlit dashboard.

This project uses TMDB-sourced data only; the former Rotten Tomatoes /
Hugging Face dataset is not used. Project 1 does not train a machine
learning or deep learning model. Its sentiment categories are approximate
labels derived from reviewer ratings, not predictions from review text.

2. PROJECT OBJECTIVES
---------------------
- Collect movie reviews and movie statistics from the TMDB API.
- Validate and clean review data before database storage.
- Preserve original API data as JSON/JSONB, not as a CSV-based dataset.
- Avoid duplicate review IDs and track first-seen and last-seen times.
- Maintain a cloud database with review and movie-history records.
- Analyze sentiment counts, ratings, review lengths, movies, and trends.
- Show interactive charts and filters through a public Streamlit dashboard.
- Run the collector on a cloud schedule without depending on the laptop.
- Establish a TMDB-only dataset for later ML and DL coursework.

3. DATA SOURCE AND SENTIMENT LABELS
----------------------------------
Data source: TMDB (The Movie Database)
Website: https://www.themoviedb.org/
API documentation: https://developer.themoviedb.org/

The collector selects trending, popular, and lower-rated movies and checks
up to three pages of reviews per selected movie. It retrieves available
review text, reviewer information, optional ratings, review timestamps,
and movie statistics such as popularity and vote counts.

Approximate rating-derived sentiment rules:
- Rating 0 through 4: Negative
- Rating greater than 4 but below 7: Neutral
- Rating 7 through 10: Positive
- Missing rating: Unlabeled

These are heuristic labels and may not match the wording of a review.
New reviews are not guaranteed on every collection run.

4. TECHNOLOGIES
---------------
Python          - Main programming language
requests        - TMDB API requests with retries and connection reuse
Pydantic        - Review data validation
pandas          - Data cleaning, transformation, and analysis
Matplotlib      - EDA and dashboard chart generation
Seaborn         - EDA plot styling
Supabase        - Cloud PostgreSQL storage and Python client
PostgreSQL JSONB- Original TMDB API response storage
Streamlit       - Interactive dashboard and welcome page
python-dotenv   - Local environment-variable loading
GitHub          - Source code repository and version history
GitHub Actions  - Scheduled cloud collector
Streamlit Cloud - Public dashboard hosting

5. ETL PIPELINE
---------------
EXTRACT: etl/collect_live.py
- Uses the TMDB API to select movies and retrieve available reviews.
- Handles selected temporary errors with retries and timeouts.
- Checks individual movies independently where possible, logs skipped
  movies, and reports the collection results.

TRANSFORM: etl/validate_tmdb.py and etl/collect_live.py
- Pydantic validates review IDs, content, movie IDs, titles, and ratings.
- Invalid records are skipped and unique review IDs are consolidated.
- Approximate sentiment labels are derived from optional reviewer ratings.

LOAD: JSON snapshots and Supabase PostgreSQL
- A timestamped JSON file is written to data/tmdb_captures/ per run.
- tmdb_reviews stores unique review records, ratings, approximate labels,
  review timestamps, first_seen_at, last_seen_at, and original JSON.
- tmdb_movie_history stores dated movie-statistics snapshots and JSON.
- Reviews are upserted by review_id to avoid duplicate database rows.

IMPORTANT: JSON captures made on a local computer remain local. Captures
written during GitHub Actions runs reside on a temporary runner and are
not permanent cloud backups unless artifact upload or external storage is
configured. Supabase database writes are separate from those files.

6. AUTOMATIC CLOUD DATA COLLECTION
----------------------------------
Workflow: .github/workflows/tmdb-collector.yml
Collector: etl/collect_live.py

GitHub Actions runs the collector using Python 3.12 and repository secrets.
The workflow supports both manual runs and an hourly cron schedule:
17 * * * *  (minute 17 of each hour, UTC)

Required GitHub Actions repository secrets:
- TMDB_READ_ACCESS_TOKEN
- SUPABASE_URL
- SUPABASE_SECRET_KEY

A scheduled workflow run was successfully observed on November 19, 2026.
In that run, 84 movies were processed, 254 unique reviews were checked,
one new review was inserted, and 253 existing reviews were rechecked.
These counts describe that single run, not the total size of the database.

The collector is scheduled in the cloud, so normal operation no longer
requires the user's laptop to remain on. GitHub scheduled jobs can be
delayed or occasionally skipped; a successful scheduled run does not
promise uninterrupted, guaranteed hourly execution.

Previous local automation: run_collector.bat and Windows Task Scheduler.
The local scheduled task was disabled to avoid duplicate collection runs.
The batch file is retained as an optional local launcher.

7. EXPLORATORY DATA ANALYSIS (EDA)
----------------------------------
Script: eda/analyze.py

EDA reads review records from Supabase and generates six PNG charts:
- 01_sentiment_distribution.png
- 02_rating_distribution.png
- 03_top_movies.png
- 04_review_lengths.png
- 05_daily_collection.png
- 06_cumulative_collection.png

Output directory: eda/results/
Reports:
- eda_summary.json: computed statistics and data-quality metrics
- eda_report.txt: readable summary and interpretation

Collection-date charts use first_seen_at (when the system first recorded
a review), not the original publication date of that review.
The EDA PNGs and reports regenerate only when analyze.py is run; they
are not automatically regenerated by each dashboard refresh or by the
current GitHub Actions collector workflow.

8. STREAMLIT DASHBOARD
----------------------
Main file: dashboard/live_app.py
Public URL: https://movie-pulse-analytics.streamlit.app/

The website starts with a dark-themed welcome page and an
"Explore Dashboard" button. The dashboard provides:
- KPI cards: total reviews, movies covered, rated reviews, average rating
- Sentiment filtering, movie filtering, search, and rating availability
- Seven visualizations:
  1. Review Trend Overview (grouped daily sentiment bars)
  2. Sentiment Mix (circular progress rings)
  3. Top Movies (review counts)
  4. Reviews by Time (weekday/time-of-day activity heatmap)
  5. Rating Distribution
  6. Review Length Distribution
  7. Cumulative Collection Trend
- Recent Reviews Snapshot and searchable Review Explorer
- Information about the project's ETL and EDA workflow
- Last-seen review timestamp displayed in the sidebar

Dashboard charts respond to selected filters. The Review Explorer also
provides an optional CSV download of filtered displayed data; the actual
ETL storage continues to use JSON and Supabase, not CSV files.

The dashboard uses periodic refresh while a browser session is active.
Refresh does not itself query TMDB or guarantee any new reviews; the
separate GitHub Actions collector updates the Supabase database.

9. PROJECT FILES
----------------
etl/collect_live.py               - TMDB collection, validation, JSON, upload
etl/validate_tmdb.py             - Pydantic validation models
eda/analyze.py                   - EDA, charts, reports
dashboard/live_app.py            - Welcome page and analytics dashboard
.github/workflows/tmdb-collector.yml - Hourly cloud collector workflow
run_collector.bat                - Optional local Windows launcher
requirements.txt                - Python package dependencies
.gitignore                      - Excludes secrets and generated local data
README.txt                      - Project documentation
eda/results/                    - Generated EDA charts and reports
data/tmdb_captures/              - Local timestamped JSON captures
.env                            - Private local credentials (not in Git)

The former initial-testing scripts test_tmdb.py, test_supabase.py, and
upload_tmdb.py were removed from the active project.

10. HOW TO RUN LOCALLY (WINDOWS)
--------------------------------
Open a PowerShell terminal in the project root folder.

Step 1: Create a virtual environment (first time only):
  python -m venv .venv

Step 2: Install dependencies:
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Step 3: Create a private .env file in the project root:
  TMDB_READ_ACCESS_TOKEN=your_tmdb_token
  SUPABASE_URL=https://your-project-id.supabase.co
  SUPABASE_SECRET_KEY=your_supabase_secret_key

Never commit the real .env file or expose credentials in screenshots.

Step 4: Prepare the two Supabase tables: tmdb_reviews and
        tmdb_movie_history, with the required schema and security policies.
        These tables are not created automatically by Python scripts.

Step 5: Run the collector manually if necessary:
  .\.venv\Scripts\python.exe etl\collect_live.py

Step 6: Generate EDA reports:
  .\.venv\Scripts\python.exe eda\analyze.py

Step 7: Run the dashboard locally:
  .\.venv\Scripts\python.exe -m streamlit run dashboard\live_app.py

Open http://localhost:8501 in a browser.

11. CLOUD DEPLOYMENT AND UPDATES
--------------------------------
Streamlit Community Cloud hosts the public dashboard using the GitHub
repository, branch main, and main file dashboard/live_app.py.
Its deployment settings contain private SUPABASE_URL and
SUPABASE_SECRET_KEY values; they must never appear in public source code.

GitHub Actions runs the separate collection workflow using the three
repository secrets listed above. The public app and cloud collector
share the same Supabase database.

To publish future source-code updates: edit locally, test, commit, and
push changes to the main branch. Streamlit Cloud normally redeploys app
changes from GitHub; scheduled collector changes take effect from the
updated workflow. A redeployment can fail if dependencies or settings
are invalid, so verify the live site and Actions logs after updates.

12. SECURITY AND LIMITATIONS
----------------------------
- Never commit .env files, Supabase secrets, or API credentials.
- Public GitHub collaborators who can edit Actions workflows must be
  trusted, because workflow changes may expose repository secrets.
- The deployed dashboard currently reads Supabase using a server-side
  privileged key. For stronger production security, replace this with
  least-privilege, read-only access and appropriate Row Level Security.
- Cloud schedule attempts are not guaranteed to run at an exact time.
- A successful run may insert zero new reviews if TMDB has no new data.
- The collector processes a selected sample of movies and review pages,
  not every review available across the whole TMDB catalog.
- Ratings are approximate sentiment proxies, not confirmed text labels.
- Follow TMDB attribution, terms, and permitted data-use requirements.
- Project 1 performs ETL and EDA; it does not train an ML or DL model.

13. FUTURE PROJECTS
-------------------
Project 2 - Machine Learning:
Use TMDB reviews to assess label quality, prepare train/test sets, and
train and evaluate scikit-learn sentiment classifiers.

Project 3 - Deep Learning:
Use TMDB review data for a PyTorch model and track experiments with MLflow.

Both projects are planned to use TMDB-only data. Sufficient data volume,
label reliability, and proper held-out evaluation must be established.

CONCLUSION
----------
Movie Pulse demonstrates live TMDB API extraction, Pydantic validation,
JSON and JSONB storage, Supabase cloud persistence, scheduled GitHub
Actions collection, Exploratory Data Analysis, and a public interactive
Streamlit analytics website.
