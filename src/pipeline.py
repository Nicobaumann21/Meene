"""Spark-Pipeline für MovieLens-Datensatz.

Liest ratings.csv, bereinigt Daten und führt einen 80/20 Train/Test-Split durch.
Lokal: data/small/ratings.csv (MovieLens-Small, ~100k).
VM:    data/ml-25m/ratings.csv (MovieLens 25M).
"""

import time
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def build_spark(app_name: str = "MovieRec") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "50")
        .getOrCreate()
    )


def load_ratings(spark: SparkSession, path: str):
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(path)
    )


def clean(df):
    return (
        df.dropna()
          .dropDuplicates(["userId", "movieId"])
          .withColumn("userId", col("userId").cast("int"))
          .withColumn("movieId", col("movieId").cast("int"))
          .withColumn("rating", col("rating").cast("float"))
    )


def main():
    project_root = Path(__file__).resolve().parent.parent
    ratings_path = project_root / "data" / "small" / "ratings.csv"

    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    print(f"Lese: {ratings_path}")
    t0 = time.time()
    df_raw = load_ratings(spark, str(ratings_path))

    print("\n=== Schema (roh) ===")
    df_raw.printSchema()
    n_raw = df_raw.count()
    print(f"Zeilen (roh): {n_raw:,}")

    df = clean(df_raw)
    n_clean = df.count()
    print(f"Zeilen (bereinigt): {n_clean:,}  (entfernt: {n_raw - n_clean:,})")

    train, test = df.randomSplit([0.8, 0.2], seed=42)
    n_train, n_test = train.count(), test.count()
    print(f"\nTrain: {n_train:,}  |  Test: {n_test:,}")

    print(f"\nLaufzeit: {time.time() - t0:.1f}s")

    spark.stop()


if __name__ == "__main__":
    main()
