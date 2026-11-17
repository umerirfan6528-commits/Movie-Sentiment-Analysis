LIVE MOVIE REVIEW SENTIMENT ANALYTICS
====================================
UNIVERSITY PROJECT 1 - ETL + EXPLORATORY DATA ANALYSIS (EDA)

1. ABOUT THE PROJECT
--------------------
Live Movie Review Sentiment Analytics is a Python university project that
collects and analyzes movie reviews and movie statistics from the TMDB
(The Movie Database) API.

The project extracts live API data, validates and processes reviews, stores
JSON snapshots, saves records in a Supabase PostgreSQL database, and performs
Exploratory Data Analysis (EDA). A Streamlit dashboard presents review
sentiments, reviewer ratings, movie statistics, and historical trends.

The active project uses only TMDB API data. The old Hugging Face / Rotten
Tomatoes dataset is not used. Project 1 does not train a machine learning
or deep learning model. Sentiment categories come from reviewer ratings
and are approximate, not manually verified predictions.

2. PROJECT OBJECTIVES
---------------------
- Fetch TMDB movie reviews and movie statistics using Python requests.
- Automatically check for new or updated information on a schedule.
- Save collected API data in JSON format instead of CSV.
- Validate movie review records using Pydantic.
- Store reviews and movie history in Supabase PostgreSQL with JSONB fields.
- Avoid duplicate review IDs and track when reviews are first and last seen.
- Analyze review counts, rating distributions, review lengths, and trends.
- Provide a Streamlit dashboard that periodically refreshes from Supabase.
- Build a TMDB-based data foundation for future ML and DL projects.

3. DATA SOURCE
--------------
Source: TMDB (The Movie Database)
Website: https://www.themoviedb.org/
API documentation: https://developer.themoviedb.org/

The collector uses TMDB endpoints for trending movies, popular movies,
movie discovery, and movie-specific reviews. Available information includes
movie IDs, titles, review text, authors, optional reviewer ratings, TMDB
popularity scores, average movie ratings, vote counts, and timestamps.

An API request may return the same information as a previous request.
New reviews or changed statistics are not guaranteed on every collection.

4. TOOLS AND TECHNOLOGIES
------------------------
Python            - Main programming language
requests          - Retrieves data from the TMDB API
Pydantic          - Validates review IDs, text, movie IDs, and ratings
pandas            - Processes and analyzes collected records
Matplotlib        - Generates EDA graphs
Seaborn           - Provides statistical visualization styling
Supabase          - Cloud PostgreSQL database and Python client
PostgreSQL JSONB  - Stores original API JSON records
Streamlit         - Interactive dashboard and periodic refresh
python-dotenv     - Loads local environment variables
Task Scheduler    - Runs the collector automatically on Windows

5. ETL PIPELINE
---------------
EXTRACT: etl/collect_live.py

The collector fetches selected trending, popular, and lower-rated movies,
then retrieves available review pages. It includes retries for selected
temporary API errors and records the collection time.

TRANSFORM: etl/validate_tmdb.py and etl/collect_live.py

Pydantic checks the required fields, including review ID, movie ID,
non-empty review text, movie title, and rating when available. Invalid
records are skipped. Duplicate review IDs are combined using their IDs.

Approximate sentiment labeling based on reviewer ratings:
- Rating 0 through 4: Negative
- Rating greater than 4 but below 7: Neutral
- Rating 7 through 10: Positive
- Missing rating: Unlabeled

These categories are derived from ratings. They are not verified text
sentiment labels and may not always reflect the wording of a review.

LOAD: Local JSON and Supabase

Each collector run saves a timestamped JSON capture to:
data/tmdb_captures/

The Supabase database contains two main tables:
- tmdb_reviews: Unique reviews, movie details, ratings, labels, review
  timestamps, collection timestamps, and original review JSON.
- tmdb_movie_history: Timestamped movie popularity, average rating,
  vote count, and original movie JSON.

The collector uses upsert to insert new reviews or update existing review
records without creating extra rows for the same review ID. Movie history
stores separate snapshots for comparisons across collection runs.

6. AUTOMATIC DATA COLLECTION
----------------------------
Launcher: run_collector.bat
Log file: data/collector.log

Windows Task Scheduler is configured to launch the collector every hour.
The batch file starts the project's Python virtual environment and writes
collector output and errors into the log. Exit code 0 means the Python
process completed successfully.

This is scheduled polling, not continuous streaming. On a local Windows
laptop, scheduled data collection depends on the computer being available
and able to run the task. A 24/7 cloud-based collector is not configured.

7. EXPLORATORY DATA ANALYSIS (EDA)
----------------------------------
File: eda/analyze.py

EDA reads the currently stored TMDB reviews from Supabase and generates:
- 01_sentiment_distribution.png
- 02_rating_distribution.png
- 03_top_movies.png
- 04_review_lengths.png
- 05_daily_collection.png
- 06_cumulative_collection.png

Reports are saved to eda/results/:
- eda_summary.json (statistical results)
- eda_report.txt (readable findings and interpretation)

Collection trends are based on first_seen_at: the date the collector first
observed each review, not necessarily the date the review was published.

The EDA script generates files when run. Its saved graphs do not
regenerate automatically every time the Streamlit dashboard refreshes.

8. STREAMLIT DASHBOARD
----------------------
File: dashboard/live_app.py

The dashboard reads TMDB records from Supabase and provides:
- Total, Positive, Negative, Neutral, and Unlabeled review counts
- Sentiment distribution
- Movie-wise selection and filtering
- Reviewer rating distribution and average rating
- Review browsing and recently collected reviews
- Last review-check time
- Daily new-review and cumulative collection graphs
- Latest TMDB movie popularity, vote count, and average rating
- Historical popularity and voting graphs for selected movies
- A movie statistics history table

The dashboard checks Supabase for updates every five minutes when the
browser session is active. Refreshing the display does not itself guarantee
that new API records exist. Data collection is handled separately by the
scheduled collector.

9. VERIFIED SAMPLE RESULTS
--------------------------
During a previous local run, Supabase contained the following TMDB data:

Total reviews:        286
Movies analyzed:      61
Positive reviews:     122
Negative reviews:      78
Neutral reviews:       52
Unlabeled reviews:     34
Rated reviews:        252
Missing ratings:       34
Empty review texts:     0
Duplicate review IDs:  0

These are results from one verified snapshot, not fixed dataset totals.
The database may grow or individual records may be updated later.

10. MAIN PROJECT FILES
----------------------
etl/collect_live.py       - TMDB extraction, validation, JSON, DB writes
etl/validate_tmdb.py     - Pydantic models for review validation
etl/test_tmdb.py         - Initial TMDB API test
etl/test_supabase.py     - Database connection test
etl/upload_tmdb.py       - Initial JSON sample upload
eda/analyze.py           - EDA statistics, charts, and reports
eda/results/             - Generated PNG charts, JSON and text reports
dashboard/live_app.py    - Supabase-connected Streamlit dashboard
data/tmdb_captures/      - Timestamped TMDB JSON snapshots
data/collector.log       - Collector execution log
run_collector.bat        - Windows Task Scheduler launch script
requirements.txt        - Required Python packages
.env                    - Private TMDB and Supabase credentials
.gitignore              - Excludes secrets, environments, generated data
README.txt              - Project documentation

11. HOW TO RUN (WINDOWS)
------------------------
Open a terminal in the main Movie_Sentiment_Analysis project folder.

Step 1: Create the Python virtual environment (first time only):
  python -m venv .venv

Step 2: Install dependencies:
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Step 3: Configure a private .env file in the main project folder:
  TMDB_READ_ACCESS_TOKEN=your_tmdb_token
  SUPABASE_URL=https://your-project-id.supabase.co
  SUPABASE_SECRET_KEY=your_supabase_secret_key

Replace the placeholders with actual credentials. Never publish the .env
file or expose the secret key in screenshots.

Step 4: Prepare the Supabase PostgreSQL tables named tmdb_reviews and
        tmdb_movie_history with the required columns, indexes, and RLS.
        A new Supabase project does not create these tables automatically.

Step 5: Run a live collection:
  .\.venv\Scripts\python.exe etl\collect_live.py

Step 6: Generate EDA reports:
  .\.venv\Scripts\python.exe eda\analyze.py

Step 7: Launch the dashboard:
  .\.venv\Scripts\python.exe -m streamlit run dashboard\live_app.py

Open http://localhost:8501 in a browser.
Press Ctrl+C in the terminal to stop Streamlit.

Step 8 (optional): Configure Windows Task Scheduler to execute
        run_collector.bat every hour using the correct local project path.

12. SECURITY AND LIMITATIONS
----------------------------
- The .env file must never be committed to Git or shared publicly.
- A Supabase secret key has privileged access and belongs only in a
  trusted backend environment; do not embed it in public client code.
- Local JSON snapshots and collector logs are excluded from Git.
- The live collector and dashboard both require internet access.
- Collection is periodic and depends on available TMDB API data.
- A successful collector run does not guarantee any new reviews.
- TMDB terms, attribution, and permitted data uses must be respected.
- Review sentiment labels are heuristic categories derived from ratings.
- The current Project 1 does not train an ML or deep learning model.

13. FUTURE PROJECTS
-------------------
Project 2 - Machine Learning:
Use the collected TMDB reviews to assess label quality, build suitable
training and test sets, and train and evaluate sentiment classifiers with
scikit-learn.

Project 3 - Deep Learning:
Use TMDB review data to train a PyTorch model and track experiments with
MLflow, while testing generalization on appropriate held-out data.

Both future projects will use TMDB-sourced data only. Sufficient data
volume, diversity, label reliability, and evaluation quality still need
to be established before model training.

CONCLUSION
----------
This university project demonstrates live API integration, ETL, JSON
storage, Pydantic validation, cloud PostgreSQL storage, scheduled data
collection, Exploratory Data Analysis, and an interactive Streamlit
dashboard. The project periodically checks for real changes in TMDB data
and reports the latest records available in Supabase.
