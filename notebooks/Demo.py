"""
Live-Demo der Film-Empfehlungen aus dem trainierten ALS-Modell.

Start auf der VM:
    source ~/venv/bin/activate
    streamlit run notebooks/Demo.py --server.port 8501 --server.headless true

Lokaler Browser-Zugriff vom Laptop:
    ssh -L 8501:localhost:8501 group6@<vm-host>
    Im Browser: http://localhost:8501
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from pyspark.ml.recommendation import ALSModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode


ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "results" / "models"
DATA_DIR = Path("~/data/ml-25m").expanduser()

st.set_page_config(
    page_title="MovieLens Empfehlungssystem",
    page_icon="🎬",
    layout="wide",
)


@st.cache_resource
def get_spark():
    return (
        SparkSession.builder
        .appName("MovieRec-Demo")
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .config("spark.driver.maxResultSize", "1g")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )


@st.cache_resource
def load_model(model_name: str):
    get_spark()
    return ALSModel.load(str(MODELS_DIR / model_name))


@st.cache_resource
def load_movies():
    spark = get_spark()
    return spark.read.csv(str(DATA_DIR / "movies.csv"), header=True, inferSchema=True)


@st.cache_resource
def load_ratings():
    spark = get_spark()
    return spark.read.csv(str(DATA_DIR / "ratings.csv"), header=True, inferSchema=True)


def get_recommendations(model, user_id: int, n: int) -> pd.DataFrame:
    spark = get_spark()
    users_df = spark.createDataFrame([(user_id,)], ["userId"])
    recs = model.recommendForUserSubset(users_df, n)
    flat = recs.select(explode("recommendations").alias("rec")).select(
        col("rec.movieId").alias("movieId"),
        col("rec.rating").alias("score"),
    )
    out = flat.join(load_movies(), on="movieId", how="left").orderBy(col("score").desc())
    return out.toPandas()


def get_user_history(user_id: int, top_n: int = 10) -> pd.DataFrame:
    user_ratings = load_ratings().filter(col("userId") == user_id)
    joined = user_ratings.join(load_movies(), on="movieId", how="left")
    return (
        joined.orderBy(col("rating").desc(), col("timestamp").desc())
              .limit(top_n)
              .toPandas()
    )


st.title("🎬 MovieLens Empfehlungssystem")
st.caption("Collaborative Filtering mit Spark MLlib (ALS) auf 25 Mio. Bewertungen")

with st.sidebar:
    st.header("Einstellungen")
    available_models = sorted(p.name for p in MODELS_DIR.iterdir() if p.is_dir())
    if not available_models:
        st.error("Keine Modelle in results/models/ gefunden.")
        st.stop()
    model_name = st.selectbox("Modell", available_models, index=len(available_models) - 1)
    n = st.slider("Anzahl Empfehlungen", min_value=5, max_value=20, value=10)
    st.divider()
    st.markdown("**Beispiel-Nutzer aus der Doku:**")
    st.code("110971  (Drama)\n73238   (Action)\n88539   (Comedy)", language="text")
    user_id_input = st.text_input("User-ID", value="110971")
    show_history = st.checkbox("Bewertungshistorie anzeigen", value=True)
    submit = st.button("Empfehlungen berechnen", type="primary", use_container_width=True)

if not submit:
    st.info("👈 User-ID wählen und auf **Empfehlungen berechnen** klicken.")
    st.stop()

try:
    user_id = int(user_id_input)
except ValueError:
    st.error("Bitte eine ganzzahlige Nutzer-ID eingeben.")
    st.stop()

with st.spinner(f"Lade Modell „{model_name}“…"):
    model = load_model(model_name)

with st.spinner(f"Berechne Empfehlungen für User {user_id}…"):
    try:
        recs_df = get_recommendations(model, user_id, n)
    except Exception as e:
        st.error(f"Fehler bei der Berechnung: {e}")
        st.stop()

if recs_df.empty:
    st.warning(
        f"Keine Empfehlungen für User {user_id} (Nutzer evtl. nicht im Trainingsset)."
    )
    st.stop()

col_l, col_r = st.columns([3, 2])

with col_l:
    st.subheader(f"Top {n} Empfehlungen für User {user_id}")
    display_df = recs_df[["title", "genres", "score"]].copy()
    display_df["score"] = display_df["score"].round(3)
    display_df.index = range(1, len(display_df) + 1)
    display_df.columns = ["Titel", "Genres", "Score"]
    st.dataframe(display_df, use_container_width=True, height=420)

with col_r:
    st.subheader("Score-Verteilung")
    chart_df = recs_df[["title", "score"]].set_index("title")
    st.bar_chart(chart_df, height=420)

if show_history:
    st.divider()
    st.subheader(f"Bewertungshistorie (Top 10) von User {user_id}")
    with st.spinner("Lade Historie…"):
        try:
            hist_df = get_user_history(user_id, top_n=10)
        except Exception as e:
            st.warning(f"Historie konnte nicht geladen werden: {e}")
            hist_df = pd.DataFrame()
    if hist_df.empty:
        st.info("Dieser Nutzer hat keine Bewertungen im Datensatz.")
    else:
        hist_display = hist_df[["title", "genres", "rating"]].copy()
        hist_display.index = range(1, len(hist_display) + 1)
        hist_display.columns = ["Titel", "Genres", "Bewertung"]
        st.dataframe(hist_display, use_container_width=True)
