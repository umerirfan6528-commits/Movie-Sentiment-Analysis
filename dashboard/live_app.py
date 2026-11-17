import os
from pathlib import Path
import time

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from supabase import create_client


# ---------------------------------------------------
# Page setup
# ---------------------------------------------------
st.set_page_config(
    page_title="Live Movie Sentiment Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials missing in .env file.")
    st.stop()


# ---------------------------------------------------
# Custom styling
# ---------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0B1020 0%, #0E1428 100%);
        color: #E5E7EB;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1020 0%, #111A2E 100%);
        border-right: 1px solid #24314B;
    }

    [data-testid="stSidebar"] * {
        color: #E5E7EB !important;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    .top-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.1rem;
    }

    .top-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }

    .metric-card {
        background: linear-gradient(180deg, #11192D 0%, #0F172A 100%);
        border: 1px solid #24314B;
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        min-height: 120px;
    }

    .metric-label {
        color: #A5B4FC;
        font-size: 0.90rem;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #F8FAFC;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .metric-note {
        color: #22C55E;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .panel-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.35rem;
    }

    .panel-subtitle {
        color: #94A3B8;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
    }

    .small-badge {
        display: inline-block;
        background: rgba(124, 58, 237, 0.16);
        color: #C4B5FD;
        border: 1px solid rgba(124, 58, 237, 0.35);
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.75rem;
        margin-right: 6px;
    }

    .sidebar-logo {
        font-size: 1.3rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 1rem;
    }

    .sidebar-section {
        color: #94A3B8;
        font-size: 0.72rem;
        letter-spacing: 1px;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
    }

    .info-box {
        background: linear-gradient(180deg, #131D34 0%, #11192D 100%);
        border: 1px solid #24314B;
        border-radius: 18px;
        padding: 14px 16px;
    }

    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background-color: #11192D !important;
        color: #F8FAFC !important;
        border: 1px solid #24314B !important;
        border-radius: 12px !important;
    }

    .stDataFrame {
        border: 1px solid #24314B;
        border-radius: 16px;
        overflow: hidden;
    }

/* Fix Streamlit white header */
header[data-testid="stHeader"],
.stAppHeader {
    background: #0B1020 !important;
    border-bottom: 1px solid #24314B !important;
}

/* Make toolbar match dark theme */
[data-testid="stToolbar"] {
    background: transparent !important;
}

/* Fix dashboard title being cut */
.block-container {
    padding-top: 4.5rem !important;
}

/* Improve main content spacing */
[data-testid="stVerticalBlock"] {
    gap: 1rem;
}

/* Premium dark sidebar navigation */
[data-testid="stSidebar"] {
    background: #0D1528 !important;
    border-right: 1px solid #24314B;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 6px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%;
    padding: 11px 12px;
    border-radius: 10px;
    border: 1px solid transparent;
    transition: background 0.2s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #1E2946;
}

[data-testid="stSidebar"] [role="radiogroup"]
label:has(input:checked) {
    background: #293473;
    border-color: #394694;
}

[data-testid="stSidebar"] [role="radiogroup"]
label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700;
}

[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-weight: 500;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] {
    margin-bottom: 5px;
}

/* Full-width sidebar navigation */
[data-testid="stSidebar"] [role="radiogroup"] {
    width: 100%;
    align-items: stretch;
    gap: 5px;
}

/* Navigation menu items */
[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex !important;
    width: 100% !important;
    box-sizing: border-box;
    padding: 12px 14px !important;
    border-radius: 9px;
    cursor: pointer;
}

/* Hide default radio circles */
[data-testid="stSidebar"] [role="radiogroup"]
label > div:first-child {
    display: none !important;
}

/* Selected navigation item */
[data-testid="stSidebar"] [role="radiogroup"]
label:has(input:checked) {
    background: #293473 !important;
    border: 1px solid #4856A3 !important;
}

/* Hover styling */
[data-testid="stSidebar"] [role="radiogroup"]
label:hover {
    background: #202C4B;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# Welcome / Landing Page
# ---------------------------------------------------

if not st.session_state.get("dashboard_opened", False):

    st.html("""
    <style>
        .stApp {
            background: linear-gradient(
                135deg,
                #E1F0F1 0%,
                #F6F2FA 52%,
                #EFE9F7 100%
            ) !important;
        }

        header[data-testid="stHeader"] {
            display: none !important;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }

        .block-container {
            padding-top: 6vh !important;
        }

        .welcome-container {
            min-height: 62vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
            position: relative;
        }

        .welcome-logo {
            width: 90px;
            height: 90px;
            border-radius: 28px;
            background: linear-gradient(
                135deg, #9076D4, #31B6A8
            );
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 43px;
            box-shadow: 0 15px 35px
                rgba(113, 104, 180, 0.20);
            margin-bottom: 28px;
        }

        .welcome-label {
            letter-spacing: 5px;
            font-size: 12px;
            font-weight: 800;
            color: #4BAE9E;
            margin-bottom: 20px;
        }

        .welcome-heading {
            font-size: clamp(42px, 6vw, 76px);
            font-weight: 800;
            color: #4C435D;
            line-height: 1.15;
            letter-spacing: -2px;
            margin-bottom: 22px;
        }

        .gradient-text {
            background: linear-gradient(
                90deg, #5E9CCF, #26B5A5
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .welcome-subtitle {
            color: #8F889E;
            font-size: 18px;
            line-height: 1.8;
            max-width: 650px;
            margin-bottom: 25px;
        }

        .color-dots {
            display: flex;
            justify-content: center;
            gap: 12px;
        }

        .color-dots span {
            width: 11px;
            height: 11px;
            border-radius: 50%;
        }

        /* Explore Dashboard button */
        [data-testid="stButton"] button {
            background: linear-gradient(
                90deg, #9075D4, #629BCF
            ) !important;
            border: 2px solid #B5CCDC !important;
            border-radius: 50px !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            padding: 15px 30px !important;
            height: auto !important;
            box-shadow: 0 12px 25px
                rgba(112, 105, 185, 0.25);
            transition: transform 0.2s ease;
        }

        [data-testid="stButton"] button:hover {
            transform: translateY(-3px);
            box-shadow: 0 16px 30px
                rgba(112, 105, 185, 0.35);
        }

            /* Premium Dark Welcome Page */

            .stApp {
                background:
                    radial-gradient(
                        circle at 20% 20%,
                        rgba(124, 58, 237, 0.14),
                        transparent 35%
                    ),
                    radial-gradient(
                        circle at 80% 75%,
                        rgba(56, 189, 248, 0.08),
                        transparent 35%
                    ),
                    linear-gradient(
                        135deg,
                        #0B1020 0%,
                        #11192D 55%,
                        #0B1020 100%
                    ) !important;
            }

            /* Main heading */
            .welcome-heading {
                color: #F8FAFC !important;
            }

            /* Gradient text */
            .gradient-text {
                background: linear-gradient(
                    90deg,
                    #A78BFA,
                    #818CF8,
                    #38BDF8
                ) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }

            /* Small brand label */
            .welcome-label {
                color: #A78BFA !important;
            }

            /* Description */
            .welcome-subtitle {
                color: #94A3B8 !important;
            }

            /* Logo */
            .welcome-logo {
                background: linear-gradient(
                    135deg,
                    #7C3AED,
                    #6366F1
                ) !important;

                box-shadow:
                    0 15px 40px rgba(124, 58, 237, 0.25);
            }

            /* Explore Dashboard button */
            [data-testid="stButton"] button {
                background: linear-gradient(
                    90deg,
                    #7C3AED,
                    #6366F1
                ) !important;

                border: 1px solid #6366F1 !important;
                color: #FFFFFF !important;

                box-shadow:
                    0 10px 30px rgba(124, 58, 237, 0.3);
            }

            [data-testid="stButton"] button:hover {
                background: linear-gradient(
                    90deg,
                    #8B5CF6,
                    #818CF8
                ) !important;
            }
        
/* Smooth Welcome Page Animations */

@keyframes welcomeFadeUp {
    from {
        opacity: 0;
        transform: translateY(25px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.welcome-logo {
    animation: welcomeFadeUp 0.8s ease-out both;
}

.welcome-label {
    animation: welcomeFadeUp 0.8s ease-out 0.15s both;
}

.welcome-heading {
    animation: welcomeFadeUp 0.9s ease-out 0.25s both;
}

.welcome-subtitle {
    animation: welcomeFadeUp 0.9s ease-out 0.4s both;
}

.color-dots {
    animation: welcomeFadeUp 0.8s ease-out 0.55s both;
}

[data-testid="stButton"] button {
    animation: welcomeFadeUp 0.8s ease-out 0.65s both;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    .welcome-logo,
    .welcome-label,
    .welcome-heading,
    .welcome-subtitle,
    .color-dots,
    [data-testid="stButton"] button {
        animation: none !important;
    }
}

/* Floating Background Particles */

.welcome-container {
    position: relative;
    isolation: isolate;
}

.welcome-container::before,
.welcome-container::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: -1;
    background-repeat: no-repeat;
}

/* Purple and blue particles */
.welcome-container::before {
    background-image:
        radial-gradient(circle, #8B5CF6 0 5px, transparent 6px),
        radial-gradient(circle, #38BDF8 0 4px, transparent 5px),
        radial-gradient(circle, #A78BFA 0 7px, transparent 8px),
        radial-gradient(circle, #6366F1 0 3px, transparent 4px);

    background-size:
        14px 14px,
        12px 12px,
        18px 18px,
        10px 10px;

    background-position:
        8% 18%,
        88% 30%,
        15% 78%,
        82% 85%;

    opacity: 0.65;
    animation: particlesFloat 8s ease-in-out infinite alternate;
}

/* Pink and teal particles */
.welcome-container::after {
    background-image:
        radial-gradient(circle, #F43F5E 0 4px, transparent 5px),
        radial-gradient(circle, #2DD4BF 0 5px, transparent 6px),
        radial-gradient(circle, #C4B5FD 0 3px, transparent 4px);

    background-size:
        12px 12px,
        14px 14px,
        10px 10px;

    background-position:
        6% 60%,
        94% 70%,
        75% 12%;

    opacity: 0.5;
    animation: particlesFloat 11s ease-in-out infinite alternate-reverse;
}

/* Gentle floating movement */
@keyframes particlesFloat {
    from {
        transform: translateY(0);
    }

    to {
        transform: translateY(-22px);
    }
}

/* Respect reduced-motion settings */
@media (prefers-reduced-motion: reduce) {
    .welcome-container::before,
    .welcome-container::after {
        animation: none !important;
    }
}

    </style>

    <div class="welcome-container">

        <div class="welcome-logo">🎬</div>

        <div class="welcome-label">
            MOVIE PULSE ANALYTICS
        </div>

        <div class="welcome-heading">
            <span class="gradient-text">
                Feel the reviews.
            </span>
            <br>
            Discover every emotion.
        </div>

        <div class="welcome-subtitle">
            Explore live movie reviews, audience
            sentiment, ratings and trends.
            Powered by TMDB data and intelligent
            analytics.
        </div>

        <div class="color-dots">
            <span style="background:#EF718A"></span>
            <span style="background:#F5A44A"></span>
            <span style="background:#8C75D5"></span>
            <span style="background:#5E9CCF"></span>
            <span style="background:#A0C64A"></span>
            <span style="background:#35B5A9"></span>
        </div>

    </div>
    """)

    left, center, right = st.columns([2, 2, 2])

    with center:
        if st.button(
            "Explore Dashboard  →",
            key="explore_dashboard",
            use_container_width=True
        ):
            st.session_state["dashboard_opened"] = True
            st.rerun()

    st.stop()


# ---------------------------------------------------
# Supabase connection
# ---------------------------------------------------
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@st.cache_data(ttl=240)
def load_reviews():
    supabase = get_supabase()

    all_rows = []
    start = 0
    batch_size = 1000

    while True:
        response = (
    supabase.table("tmdb_reviews")
    .select(
        "review_id,movie_id,movie_title,author,"
        "review_text,rating,sentiment_label,"
        "review_created_at,review_updated_at,"
        "first_seen_at,last_seen_at"
    )
    .order("review_id")
    .range(start, start + batch_size - 1)
    .execute()
)


        rows = response.data or []

        if not rows:
            break

        all_rows.extend(rows)

        if len(rows) < batch_size:
            break

        start += batch_size

    df = pd.DataFrame(all_rows)

    if df.empty:
        return df

    # Ensure columns exist
    expected_columns = [
        "review_id", "movie_id", "movie_title", "author",
        "review_text", "rating", "sentiment_label",
        "review_created_at", "review_updated_at",
        "first_seen_at", "last_seen_at"
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df["movie_title"] = df["movie_title"].fillna("Unknown Movie")
    df["author"] = df["author"].fillna("Unknown")
    df["review_text"] = df["review_text"].fillna("")
    df["sentiment_label"] = df["sentiment_label"].fillna("Unlabeled")
    df["sentiment_label"] = df["sentiment_label"].replace("", "Unlabeled")

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    for col in ["review_created_at", "review_updated_at", "first_seen_at", "last_seen_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True).dt.tz_convert(None)

    # Best date to use for trends
    df["event_time"] = df["first_seen_at"].fillna(df["review_created_at"]).fillna(df["last_seen_at"])
    df["event_date"] = pd.to_datetime(df["event_time"], errors="coerce").dt.date
    df["event_hour"] = pd.to_datetime(df["event_time"], errors="coerce").dt.hour

    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df["weekday"] = pd.to_datetime(df["event_time"], errors="coerce").dt.day_name().str[:3]
    df["weekday"] = pd.Categorical(df["weekday"], categories=weekday_order, ordered=True)

    return df.sort_values(by="event_time", ascending=False).reset_index(drop=True)


# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------
def metric_card(title, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def styled_axes(ax):
    ax.set_facecolor("#11192D")
    for spine in ax.spines.values():
        spine.set_color("#24314B")
    ax.tick_params(colors="#CBD5E1")
    ax.title.set_color("#F8FAFC")
    ax.xaxis.label.set_color("#CBD5E1")
    ax.yaxis.label.set_color("#CBD5E1")
    ax.grid(color="#24314B", alpha=0.45)



def plot_trend_chart(data):
    """Display review collection trends as grouped bars."""

    # Count reviews by date and sentiment
    daily = (
        data.dropna(subset=["event_date"])
        .groupby(["event_date", "sentiment_label"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
        .tail(10)
    )

    fig, ax = plt.subplots(
        figsize=(10, 4.5),
        facecolor="#11192D"
    )

    ax.set_facecolor("#11192D")

    if daily.empty:
        ax.text(
            0.5, 0.5,
            "No collection data available",
            ha="center",
            va="center",
            color="#CBD5E1"
        )
        ax.axis("off")

    else:
        sentiments = [
            "Positive",
            "Negative",
            "Neutral",
            "Unlabeled"
        ]

        colors = {
            "Positive": "#8B5CF6",
            "Negative": "#F43F5E",
            "Neutral": "#38BDF8",
            "Unlabeled": "#64748B"
        }

        positions = list(range(len(daily)))
        bar_width = 0.19

        for i, sentiment in enumerate(sentiments):

            values = (
                daily[sentiment]
                if sentiment in daily.columns
                else [0] * len(daily)
            )

            bar_positions = [
                x + (i - 1.5) * bar_width
                for x in positions
            ]

            ax.bar(
                bar_positions,
                values,
                width=bar_width,
                label=sentiment,
                color=colors[sentiment],
                alpha=0.95
            )

        # Axis styling
        ax.set_xticks(positions)
        ax.set_xticklabels([
            pd.Timestamp(date).strftime("%d %b")
            for date in daily.index
        ])

        ax.set_ylabel("Number of Reviews")

        ax.grid(
            axis="y",
            color="#293551",
            alpha=0.5
        )

        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(colors="#CBD5E1")
        ax.yaxis.label.set_color("#CBD5E1")

        # Professional legend
        legend = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.14),
            ncol=4,
            frameon=False,
            fontsize=9
        )

        for text in legend.get_texts():
            text.set_color("#E5E7EB")

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)




def plot_sentiment_donut(data):
    """Display sentiment percentages as circular rings."""

    from matplotlib.patches import Patch

    sentiments = [
        "Positive", "Negative", "Neutral", "Unlabeled"
    ]

    colors = {
        "Positive": "#8B5CF6",
        "Negative": "#F43F5E",
        "Neutral": "#38BDF8",
        "Unlabeled": "#64748B"
    }

    counts = (
        data["sentiment_label"]
        .value_counts()
        .reindex(sentiments, fill_value=0)
    )

    total = int(counts.sum())

    fig, ax = plt.subplots(
        figsize=(5.5, 4.5),
        facecolor="#11192D"
    )

    ax.set_facecolor("#11192D")

    if total == 0:
        ax.text(
            0, 0, "No reviews available",
            ha="center", va="center",
            color="#CBD5E1"
        )
    else:
        # Draw four circular progress rings
        for i, sentiment in enumerate(sentiments):

            count = int(counts[sentiment])
            radius = 1.0 - i * 0.18

            ax.pie(
                [count, total - count],
                radius=radius,
                startangle=90,
                counterclock=False,
                colors=[
                    colors[sentiment],
                    "#26334A"
                ],
                wedgeprops={
                    "width": 0.12,
                    "edgecolor": "#11192D",
                    "linewidth": 2
                }
            )

        # Total reviews in the center
        ax.text(
            0, 0.05, f"{total:,}",
            ha="center", va="center",
            fontsize=19,
            fontweight="bold",
            color="#FFFFFF"
        )

        ax.text(
            0, -0.11, "REVIEWS",
            ha="center", va="center",
            fontsize=8,
            color="#94A3B8"
        )

        # Legend showing actual percentages
        legend_items = [
            Patch(
                facecolor=colors[sentiment],
                label=(
                    f"{sentiment}: "
                    f"{counts[sentiment] / total * 100:.0f}%"
                )
            )
            for sentiment in sentiments
        ]

        fig.legend(
            handles=legend_items,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.01),
            ncol=2,
            frameon=False,
            labelcolor="#E5E7EB",
            fontsize=9
        )

    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(rect=[0, 0.15, 1, 1])

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)




def plot_top_movies(data):
    """Display top movies with modern horizontal bars."""

    top_movies = (
        data["movie_title"]
        .value_counts()
        .head(8)
    )

    fig, ax = plt.subplots(
        figsize=(8, 4.5),
        facecolor="#11192D"
    )

    ax.set_facecolor("#11192D")

    if top_movies.empty:
        ax.text(
            0.5, 0.5,
            "No movies available",
            ha="center",
            va="center",
            color="#CBD5E1"
        )
        ax.axis("off")

    else:
        # Shorten long movie titles for readability
        movie_names = [
            name[:25] + "..." if len(name) > 25 else name
            for name in top_movies.index
        ]

        colors = [
            "#8B5CF6",
            "#7C3AED",
            "#6366F1",
            "#4F46E5",
            "#818CF8",
            "#6366F1",
            "#7C3AED",
            "#8B5CF6"
        ]

        bars = ax.barh(
            movie_names,
            top_movies.values,
            color=colors,
            height=0.55
        )

        # Highest review count at the top
        ax.invert_yaxis()

        # Show review counts at the end of bars
        for bar in bars:
            width = bar.get_width()

            ax.text(
                width + 0.3,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)}",
                va="center",
                color="#E5E7EB",
                fontsize=10
            )

        ax.set_xlim(
            0,
            max(top_movies.values) * 1.2 + 1
        )

        ax.set_xlabel(
            "Number of Reviews",
            color="#CBD5E1"
        )

        ax.grid(
            axis="x",
            color="#293551",
            alpha=0.3
        )

        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(
            axis="both",
            colors="#CBD5E1",
            labelsize=9
        )

    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def plot_rating_distribution(data):
    """Show reviewer rating distribution."""

    ratings = pd.to_numeric(
        data["rating"],
        errors="coerce"
    ).dropna()

    fig, ax = plt.subplots(
        figsize=(8, 4.5),
        facecolor="#11192D"
    )

    ax.set_facecolor("#11192D")

    if ratings.empty:
        ax.text(
            0.5, 0.5,
            "No rated reviews available",
            ha="center",
            va="center",
            transform=ax.transAxes,
            color="#CBD5E1"
        )
    else:
        ax.hist(
            ratings,
            bins=20,
            range=(0, 10),
            color="#8B5CF6",
            edgecolor="#11192D"
        )

        ax.set_xlim(0, 10)

        ax.set_xlabel("Rating (0-10)")
        ax.set_ylabel("Number of Reviews")

        ax.grid(
            axis="y",
            color="#293551",
            alpha=0.4
        )

        ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(colors="#CBD5E1")
    ax.xaxis.label.set_color("#CBD5E1")
    ax.yaxis.label.set_color("#CBD5E1")

    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def plot_review_length_distribution(data):
    """Show distribution of review lengths in words."""

    word_counts = (
        data["review_text"]
        .fillna("")
        .astype(str)
        .str.split()
        .str.len()
    )

    fig, ax = plt.subplots(
        figsize=(8, 4.5),
        facecolor="#11192D"
    )

    ax.set_facecolor("#11192D")

    if word_counts.empty:
        ax.text(
            0.5, 0.5,
            "No reviews available",
            ha="center",
            va="center",
            transform=ax.transAxes,
            color="#CBD5E1"
        )
    else:
        ax.hist(
            word_counts,
            bins=20,
            color="#38BDF8",
            edgecolor="#11192D"
        )

        ax.set_xlabel("Number of Words")
        ax.set_ylabel("Number of Reviews")

        ax.grid(
            axis="y",
            color="#293551",
            alpha=0.4
        )

        ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(colors="#CBD5E1")
    ax.xaxis.label.set_color("#CBD5E1")
    ax.yaxis.label.set_color("#CBD5E1")

    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def plot_cumulative_collection(data):
    """Show total collected reviews over time."""

    collection_dates = pd.to_datetime(
        data["first_seen_at"],
        errors="coerce"
    ).dropna()

    fig, ax = plt.subplots(
        figsize=(10, 4.5),
        facecolor="#11192D"
    )

    ax.set_facecolor("#11192D")

    if collection_dates.empty:
        ax.text(
            0.5, 0.5,
            "No collection history available",
            ha="center",
            va="center",
            transform=ax.transAxes,
            color="#CBD5E1"
        )
        ax.axis("off")

    else:
        daily_counts = (
            collection_dates.dt.floor("D")
            .value_counts()
            .sort_index()
            .asfreq("D", fill_value=0)
        )

        cumulative = daily_counts.cumsum()

        ax.plot(
            cumulative.index,
            cumulative.values,
            color="#8B5CF6",
            linewidth=2.5,
            marker="o",
            markersize=5
        )

        ax.fill_between(
            cumulative.index,
            cumulative.values,
            color="#8B5CF6",
            alpha=0.15
        )

        ax.set_xlabel("Collection Date (UTC)")
        ax.set_ylabel("Total Reviews Collected")

        ax.grid(
            axis="y",
            color="#293551",
            alpha=0.4
        )

        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(colors="#CBD5E1")
        ax.xaxis.label.set_color("#CBD5E1")
        ax.yaxis.label.set_color("#CBD5E1")

        fig.autofmt_xdate(rotation=30)

    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def plot_time_heatmap(data):
    """Show review collection activity using colored tiles."""

    from matplotlib.patches import FancyBboxPatch

    # Use the timestamp when reviews were collected
    dates = pd.to_datetime(
        data["first_seen_at"],
        errors="coerce"
    ).dropna()

    # Create a 6 x 7 activity matrix
    activity = pd.DataFrame(
        0,
        index=range(6),
        columns=range(7)
    )

    for date in dates:
        day = date.weekday()
        time_slot = date.hour // 4
        activity.loc[time_slot, day] += 1

    days = [
        "Mon", "Tue", "Wed", "Thu",
        "Fri", "Sat", "Sun"
    ]

    time_labels = [
        "00–04", "04–08", "08–12",
        "12–16", "16–20", "20–24"
    ]

    fig, ax = plt.subplots(
        figsize=(8, 4.5),
        facecolor="#11192D"
    )

    ax.set_facecolor("#11192D")

    max_count = activity.to_numpy().max()

    # Draw individual rounded tiles
    for row in range(6):
        for col in range(7):

            count = int(activity.loc[row, col])

            if max_count == 0 or count == 0:
                color = "#1B2640"
            else:
                intensity = count / max_count

                if intensity < 0.25:
                    color = "#303C81"
                elif intensity < 0.50:
                    color = "#4D54CB"
                elif intensity < 0.75:
                    color = "#6366F1"
                else:
                    color = "#8B5CF6"

            tile = FancyBboxPatch(
                (col + 0.06, row + 0.06),
                0.88,
                0.88,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                linewidth=0,
                facecolor=color
            )

            ax.add_patch(tile)

            ax.text(
                col + 0.5,
                row + 0.5,
                str(count),
                ha="center",
                va="center",
                color="#FFFFFF",
                fontsize=10,
                fontweight="bold"
            )

    ax.set_xlim(0, 7)
    ax.set_ylim(6, 0)

    ax.set_xticks(
        [i + 0.5 for i in range(7)]
    )
    ax.set_xticklabels(days)

    ax.set_yticks(
        [i + 0.5 for i in range(6)]
    )
    ax.set_yticklabels(time_labels)

    ax.xaxis.tick_top()

    ax.tick_params(
        axis="both",
        colors="#CBD5E1",
        length=0,
        labelsize=9,
        pad=9
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_aspect("auto")

    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)



# ---------------------------------------------------
# Load data
# ---------------------------------------------------

# Automatically refresh the dashboard every 5 minutes
@st.fragment(run_every="5m")
def auto_refresh_dashboard():
    current_time = time.monotonic()

    if "last_dashboard_refresh" not in st.session_state:
        st.session_state["last_dashboard_refresh"] = current_time

    elif current_time - st.session_state["last_dashboard_refresh"] >= 295:
        st.session_state["last_dashboard_refresh"] = current_time
        st.rerun()


auto_refresh_dashboard()

df = load_reviews()

if df.empty:
    st.warning("No review data found in Supabase.")
    st.stop()


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
st.sidebar.markdown('<div class="sidebar-logo">🎬 Movie Pulse</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-section">MAIN MENU</div>', unsafe_allow_html=True)

  
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Review Explorer", "About Project"],
    format_func=lambda item: {
        "Dashboard": "📊 Dashboard",
        "Review Explorer": "🔎 Review Explorer",
        "About Project": "ℹ️ About Project"
    }[item],

    label_visibility="collapsed"
)


st.sidebar.markdown('<div class="sidebar-section">FILTERS</div>', unsafe_allow_html=True)

all_sentiments = ["All", "Positive", "Negative", "Neutral", "Unlabeled"]
selected_sentiment = st.sidebar.selectbox("Sentiment", all_sentiments)

movie_list = ["All"] + sorted(df["movie_title"].dropna().unique().tolist())
selected_movie = st.sidebar.selectbox("Movie", movie_list)

search_text = st.sidebar.text_input("Search Review Text", placeholder="e.g. amazing")

rating_filter = st.sidebar.selectbox(
    "Rating Filter",
    ["All", "Rated only", "Unrated only"]
)

st.sidebar.markdown('<div class="sidebar-section">LIVE STATUS</div>', unsafe_allow_html=True)

last_sync = df["last_seen_at"].max()
last_sync_text = last_sync.strftime("%d %b %Y, %I:%M %p") if pd.notna(last_sync) else "Unavailable"

st.sidebar.markdown(
    f"""
    <div class="info-box">
        <div style="font-size:0.9rem; color:#C4B5FD; margin-bottom:6px;">Database Status</div>
        <div style="font-size:1.4rem; font-weight:700; color:#F8FAFC;">Live</div>
        <div style="font-size:0.85rem; color:#94A3B8; margin-top:8px;">
            Last sync: {last_sync_text}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------
# Apply filters
# ---------------------------------------------------
filtered = df.copy()

if selected_sentiment != "All":
    filtered = filtered[filtered["sentiment_label"] == selected_sentiment]

if selected_movie != "All":
    filtered = filtered[filtered["movie_title"] == selected_movie]


if search_text:
    filtered = filtered[
        filtered["review_text"].str.contains(
            search_text,
            case=False,
            na=False,
            regex=False
        )
    ]


if rating_filter == "Rated only":
    filtered = filtered[filtered["rating"].notna()]
elif rating_filter == "Unrated only":
    filtered = filtered[filtered["rating"].isna()]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


# ---------------------------------------------------
# Header
# ---------------------------------------------------
st.markdown('<div class="top-title">Live Movie Sentiment Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="top-subtitle">Dark analytics dashboard powered by TMDB API, Supabase and Streamlit</div>',
    unsafe_allow_html=True
)

badge_col1, badge_col2, badge_col3 = st.columns([2, 2, 6])
with badge_col1:
    st.markdown('<span class="small-badge">Live TMDB Data</span>', unsafe_allow_html=True)
with badge_col2:
    st.markdown('<span class="small-badge">Auto Refresh Pipeline</span>', unsafe_allow_html=True)


# ---------------------------------------------------
# Pages
# ---------------------------------------------------
if page == "Dashboard":
    # Metrics
    total_reviews = len(filtered)
    total_movies = filtered["movie_title"].nunique()
    rated_reviews = filtered["rating"].notna().sum()
    avg_rating = filtered["rating"].mean()

    positive_count = (filtered["sentiment_label"] == "Positive").sum()
    negative_count = (filtered["sentiment_label"] == "Negative").sum()
    neutral_count = (filtered["sentiment_label"] == "Neutral").sum()

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        metric_card("Total Reviews", f"{total_reviews:,}", f"{positive_count:,} positive reviews")
    with m2:
        metric_card("Movies Covered", f"{total_movies:,}", f"{negative_count:,} negative reviews")
    with m3:
        metric_card("Rated Reviews", f"{rated_reviews:,}", f"{neutral_count:,} neutral reviews")
    with m4:
        metric_card("Average Rating", f"{avg_rating:.2f}/10" if pd.notna(avg_rating) else "N/A", "Live database metrics")

    st.write("")

    # Row 1
    c1, c2 = st.columns([2, 1])

    with c1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Review Trend Overview</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-subtitle">How review collection changes over time</div>', unsafe_allow_html=True)
            plot_trend_chart(filtered)

    with c2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Sentiment Mix</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-subtitle">Distribution of Positive, Negative, Neutral and Unlabeled reviews</div>', unsafe_allow_html=True)
            plot_sentiment_donut(filtered)

    # Row 2
    c3, c4 = st.columns([1, 1])

    with c3:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Top Movies</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-subtitle">Movies receiving the highest number of reviews</div>', unsafe_allow_html=True)
            plot_top_movies(filtered)

    with c4:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Reviews by Time</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-subtitle">Activity heatmap by weekday and hour</div>', unsafe_allow_html=True)
            plot_time_heatmap(filtered)
    
    # Row 3: Rating and Review Length Distribution
    st.write("")

    c5, c6 = st.columns([1, 1])

    with c5:
        with st.container(border=True):
            st.markdown(
                '<div class="panel-title">Rating Distribution</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="panel-subtitle">Distribution of reviewer ratings from 0 to 10</div>',
                unsafe_allow_html=True
            )
            plot_rating_distribution(filtered)

    with c6:
        with st.container(border=True):
            st.markdown(
                '<div class="panel-title">Review Length Distribution</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="panel-subtitle">Distribution of review lengths in words</div>',
                unsafe_allow_html=True
            )
            plot_review_length_distribution(filtered)

    # Row 4: Cumulative Collection Trend
    st.write("")

    with st.container(border=True):
        st.markdown(
            '<div class="panel-title">Cumulative Collection Trend</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="panel-subtitle">Growth of collected reviews over time</div>',
            unsafe_allow_html=True
        )
        plot_cumulative_collection(filtered)


    # Row 3
    st.write("")
    with st.container(border=True):
        st.markdown('<div class="panel-title">Recent Reviews Snapshot</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-subtitle">Latest records currently available in the live dataset</div>', unsafe_allow_html=True)

        preview = filtered[
            ["movie_title", "author", "sentiment_label", "rating", "review_text", "last_seen_at"]
        ].copy()

        preview["review_text"] = preview["review_text"].str.slice(0, 140) + "..."
        preview = preview.head(12)

        st.dataframe(preview, use_container_width=True, hide_index=True)

elif page == "Review Explorer":
    st.markdown("### Review Explorer")
    st.caption("Search and inspect the live TMDB review dataset.")

    display_df = filtered[
        ["movie_title", "author", "sentiment_label", "rating", "review_text", "review_created_at", "last_seen_at"]
    ].copy()

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Reviews",
        data=csv_data,
        file_name="filtered_tmdb_reviews.csv",
        mime="text/csv"
    )

elif page == "About Project":
    st.markdown("### About This Project")
    st.write("""
This is a live movie review analytics dashboard built for your university ETL + EDA project.

**Project workflow**
- Extract live movie review data from the TMDB API
- Validate data using Pydantic
- Store cleaned records in Supabase
- Save JSON snapshots locally
- Auto-update data using Task Scheduler
- Visualize the live data in Streamlit

**Current dashboard sections**
- Dark themed analytics layout
- KPI metric cards
- Review trend analysis
- Sentiment donut chart
- Top movies chart
- Time heatmap
- Review explorer with filters
""")

    st.info("This redesigned dashboard changes the UI only. Your TMDB, Supabase and auto-collection system remain the same.")