# Movie Recommender — DHBW Projekt 8

Collaborative-Filtering-Empfehlungssystem mit **Spark MLlib (ALS)** auf dem **MovieLens 25M**-Datensatz.

## Stack
- Python 3.11
- PySpark 3.5.0
- Pandas, Matplotlib, Jupyter
- Java 17 (für Spark)

## Quickstart (lokal, MovieLens-Small)

```bash
# Virtual Env aktivieren
source .venv/bin/activate

# Pipeline laufen lassen
python src/pipeline.py
```

## Struktur

```
movie-recommender/
├── data/
│   ├── small/        # MovieLens-Small (100k) — lokal entwickeln
│   └── ml-25m/       # MovieLens 25M — auf VM
├── docs/             # Dokumentation
├── notebooks/        # Jupyter-Notebooks
└── src/              # Pipeline-Code
```

Siehe [`docs/setup.md`](docs/setup.md) für VM-Einrichtung.
