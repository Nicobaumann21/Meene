# Movie Recommender — DHBW Projekt 8

Collaborative-Filtering-Empfehlungssystem mit **Spark MLlib (ALS)** auf dem **MovieLens 25M**-Datensatz.

**Team:** Nico Baumann, Marco Weber, Lavinia Lauer

## Stack

- Python 3.12 (auf VM) / 3.11 (lokal)
- PySpark 3.5.0
- Java 17 (für Spark)
- Pandas, Matplotlib, Jupyter

## Repo-Struktur

```
movie-recommender/
├── data/               # NICHT im Repo — auf VM unter ~/data/ml-25m/
├── docs/               # Dokumentation (Kapitel 2.4, 3.3, 4.1, 4.2, 4.5)
├── src/
│   └── pipeline.py     # Spark-Pipeline (Einlesen, Bereinigung, Train/Test-Split)
└── README.md
```

---

## Loslegen auf der VM

> **Hinweis:** VM (`group6@ubuntu`), Java, Python, venv (`~/venv/`), Datensatz (`~/data/ml-25m/`) und dieses Repo (`~/movie-recommender/`) sind bereits eingerichtet. Wer eine zweite VM aufsetzen will: komplette Anleitung in [`docs/4.1-setup.md`](docs/4.1-setup.md).

**Jedes Mal beim Einsteigen:**

```bash
# Aktuellen Stand vom Repo holen
cd ~/movie-recommender
git pull

# Virtuelle Umgebung aktivieren (in jeder neuen Shell!)
source ~/venv/bin/activate
```

Am `(venv)`-Präfix im Prompt erkennt ihr, dass die venv aktiv ist.

**Pipeline laufen lassen (Smoke-Test mit 25M-Datensatz):**

```bash
python src/pipeline.py \
    --ratings ~/data/ml-25m/ratings.csv \
    --driver-memory 6g \
    --max-result-size 2g \
    --shuffle-partitions 100
```

Läuft ca. 95 s durch. Erwartete Ausgabe am Ende: `Train: 19.998.878 | Test: 5.001.217`.

**Jupyter Notebook mit Port-Forwarding** (für interaktives Arbeiten):

```bash
# Auf der VM:
jupyter notebook --no-browser --port=8888

# Auf eurem Laptop in einem neuen Terminal:
ssh -L 8888:localhost:8888 group6@<vm-host>
```

Anschließend die Token-URL von Jupyter im Browser eures Laptops öffnen.

---

## Worauf ihr beim Coden achten müsst

### RAM-Limit (8 GB)
Die VM ist knapp dimensioniert. Wenn ihr eigenen Spark-Code schreibt:
- **Spark-Konfiguration nicht weiter aufdrehen** als bei den oben gezeigten Werten (6g Driver, 2g maxResult, 100 Partitionen). Mehr riskiert OOM.
- **`df.cache()` mit Bedacht** — bei 25M Zeilen kann der Cache schnell zum Engpass werden. Nur cachen, was wirklich mehrfach gebraucht wird.
- **`toPandas()` auf großen DataFrames vermeiden** — zieht alles in den Driver-RAM. Erst aggregieren oder filtern, dann konvertieren.

### Datensätze nicht ins Repo committen
`.gitignore` hat die `data/`-Pfade schon drin. Achtet trotzdem darauf, keine CSVs aus Versehen mit `git add .` zu adden.

### Spark-Startup dauert
Der erste Spark-Start dauert ~20–40 Sekunden (JVM-Hochfahren). Nicht ungeduldig abbrechen.

### Git-Workflow
Da wir auf derselben VM und im selben Repo arbeiten — vermeidet Konflikte:
- Vor dem Anfangen immer `git pull`
- Arbeitet auf eigenen Branches: `git checkout -b feature/als-training`
- Push: `git push -u origin feature/als-training`
- Auf GitHub Pull Request, dann Merge in `main`
- Direkt auf `main` pushen vermeiden

---

## Aktueller Stand

| Person | Aufgaben | Status |
|--------|----------|--------|
| **Nico (A)** | Infrastruktur, Datenpipeline, VM-Setup | ✅ Fertig |
| **Marco / Lavinia (B/C)** | ALS-Training (4.3), Top-N-Empfehlungen (4.4), Evaluation & Tuning (4.5), Visualisierung (4.6) | Offen |

Die Pipeline (`src/pipeline.py`) liefert bereits sauber bereinigte `train`- und `test`-DataFrames, die ihr direkt für das ALS-Training verwenden könnt.

---

## Dokumentation

Ausführliche Doku in [`docs/`](docs/):

- [`2.4-datensatz.md`](docs/2.4-datensatz.md) — MovieLens 25M (Inhalt, Kennzahlen)
- [`3.3-tech-stack.md`](docs/3.3-tech-stack.md) — Technologie-Stack & Begründung
- [`4.1-setup.md`](docs/4.1-setup.md) — VM-Setup Schritt für Schritt (für Neueinrichtung)
- [`4.2-datenvorverarbeitung.md`](docs/4.2-datenvorverarbeitung.md) — Pipeline-Bereinigung
- [`performance.md`](docs/performance.md) — Laufzeitmessungen (Kapitel 4.5)
- [`literatur.md`](docs/literatur.md) — Quellen
- [`ki-nutzung.md`](docs/ki-nutzung.md) — KI-Nutzungs-Hinweis
