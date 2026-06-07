"""Spark-Pipeline für MovieLens-Datensatz.

Liest ratings.csv, bereinigt Daten, führt einen 80/20 Train/Test-Split durch
und gibt Laufzeitkennzahlen aus.

Beispiele:
    # Lokal (MovieLens-Small, Default-Pfad)
    python src/pipeline.py

    # VM mit 25M-Datensatz und getunter Konfiguration
    python src/pipeline.py \\
        --ratings ~/data/ml-25m/ratings.csv \\
        --driver-memory 6g \\
        --max-result-size 2g \\
        --shuffle-partitions 100
"""

import argparse
import time
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parent.parent
    default_ratings = project_root / "data" / "small" / "ratings.csv"

    parser = argparse.ArgumentParser(description="MovieLens Spark-Pipeline")
    parser.add_argument(
        "--ratings",
        default=str(default_ratings),
        help="Pfad zu ratings.csv (Default: data/small/ratings.csv)",
    )
    parser.add_argument("--driver-memory", default="4g", help="spark.driver.memory")
    parser.add_argument("--max-result-size", default="1g", help="spark.driver.maxResultSize")
    parser.add_argument("--shuffle-partitions", type=int, default=50, help="spark.sql.shuffle.partitions")
    parser.add_argument("--app-name", default="MovieRec")
    return parser.parse_args()


def build_spark(args: argparse.Namespace) -> SparkSession:
    return (
        SparkSession.builder
        .appName(args.app_name)
        .config("spark.driver.memory", args.driver_memory)
        .config("spark.driver.maxResultSize", args.max_result_size)
        .config("spark.sql.shuffle.partitions", str(args.shuffle_partitions))
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
    args = parse_args()
    ratings_path = Path(args.ratings).expanduser()

    if not ratings_path.exists():
        raise FileNotFoundError(f"ratings.csv nicht gefunden: {ratings_path}")

    spark = build_spark(args)
    spark.sparkContext.setLogLevel("WARN")

    print(f"Lese: {ratings_path}")
    print(f"Spark-Config: driver-memory={args.driver_memory}, "
          f"max-result-size={args.max_result_size}, "
          f"shuffle-partitions={args.shuffle_partitions}")

    t_total = time.time()

    t0 = time.time()
    df_raw = load_ratings(spark, str(ratings_path))
    print("\n=== Schema (roh) ===")
    df_raw.printSchema()
    n_raw = df_raw.count()
    print(f"Zeilen (roh):        {n_raw:>12,}    [{time.time()-t0:.1f}s]")

    t0 = time.time()
    df = clean(df_raw)
    n_clean = df.count()
    print(f"Zeilen (bereinigt):  {n_clean:>12,}    [{time.time()-t0:.1f}s]   "
          f"(entfernt: {n_raw - n_clean:,})")

    t0 = time.time()
    train, test = df.randomSplit([0.8, 0.2], seed=42)
    n_train, n_test = train.count(), test.count()
    print(f"Train:               {n_train:>12,}    [{time.time()-t0:.1f}s]")
    print(f"Test:                {n_test:>12,}")

    print(f"\nGesamtlaufzeit:      {time.time() - t_total:>12.1f}s")

    spark.stop()


if __name__ == "__main__":
    main()
