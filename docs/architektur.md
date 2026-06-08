# Architektur des Empfehlungssystems

Das Diagramm zeigt den Datenfluss von der Rohdatenquelle (MovieLens 25M) über die Spark-Pipeline bis zu den finalen Top-N-Empfehlungen und Visualisierungen.

## Architektur-Diagramm (Mermaid)

```mermaid
flowchart TB
    subgraph Quelle["Datenquelle: MovieLens 25M"]
        R["ratings.csv<br/>25 Mio. Bewertungen<br/>userId, movieId, rating, timestamp"]
        M["movies.csv<br/>62.000 Filme<br/>movieId, title, genres"]
    end

    subgraph Spark["Apache Spark 3.5 (PySpark) auf Ubuntu-VM"]
        direction TB
        Load["1. Laden<br/>SparkSession + DataFrame"]
        Clean["2. Bereinigung<br/>dropna, Integer-Cast,<br/>Duplikate entfernen"]
        Split["3. Train/Test-Split<br/>80 / 20, seed=42"]
        ALS["4. ALS-Training<br/>rank, regParam, maxIter,<br/>coldStartStrategy=drop"]
        CV["5. Hyperparameter-Tuning<br/>CrossValidator + ParamGrid"]
        Eval["6. Evaluation<br/>RMSE auf Test-Set"]
        Rec["7. Top-N-Empfehlung<br/>recommendForAllUsers(10)"]

        Load --> Clean --> Split
        Split -->|Train-Set| ALS
        ALS --> CV
        CV --> Eval
        Split -->|Test-Set| Eval
        CV --> Rec
    end

    subgraph Output["Ergebnis & Auswertung"]
        Model["Gespeichertes Modell<br/>results/models/als_25m_final"]
        Recs["Empfehlungsliste<br/>User -> Top-10 Filme"]
        Plots["Visualisierungen<br/>(Pandas + Matplotlib)<br/>RMSE-Kurve, Score-Verteilung"]
    end

    subgraph VM["Ubuntu 24.04 VM"]
        Specs["4 vCPU, 8 GB RAM<br/>Spark-Driver: 6g<br/>Shuffle-Partitions: 100"]
    end

    R --> Load
    M -.Join für Titel.-> Rec
    Rec --> Recs
    ALS --> Model
    Eval --> Plots
    Spark -.läuft auf.-> VM

    classDef source fill:#e3f2fd,stroke:#1565c0,color:#000
    classDef process fill:#fff3e0,stroke:#e65100,color:#000
    classDef output fill:#e8f5e9,stroke:#2e7d32,color:#000
    classDef env fill:#f3e5f5,stroke:#6a1b9a,color:#000

    class R,M source
    class Load,Clean,Split,ALS,CV,Eval,Rec process
    class Model,Recs,Plots output
    class Specs env
```

## Komponentenbeschreibung

| Komponente | Verantwortung | Code/Artefakt |
|---|---|---|
| **Datenquelle** | Eingabe-CSVs (Ratings + Filme) | `data/ml-25m/` |
| **Laden** | CSV → Spark-DataFrame | `src/pipeline.py` |
| **Bereinigung** | Null-Werte droppen, Cast nach Integer, Duplikate raus | `src/pipeline.py` |
| **Train/Test-Split** | 80/20 mit festem Seed (Reproduzierbarkeit) | `src/pipeline.py` |
| **ALS-Training** | Matrix-Faktorisierung (Spark MLlib) | `notebooks/03_als_baseline.ipynb` |
| **Tuning** | CrossValidator über Parameter-Grid (rank, regParam) | `notebooks/04_tuning.ipynb` |
| **Evaluation** | RMSE auf Test-Set | `notebooks/03_als_baseline.ipynb` |
| **Top-N-Empfehlung** | `recommendForAllUsers(10)` + Join mit `movies.csv` | `notebooks/05_recommendations.ipynb` |
| **Modell speichern** | Persistiertes ALS-Modell für Demo | `results/models/als_25m_final/` |
| **Visualisierung** | Pandas + Matplotlib | `results/figures/` |

## Datenfluss in einem Satz

`ratings.csv` (25 Mio.) wird in Spark eingelesen, bereinigt, in Train/Test gesplittet; das ALS-Modell wird auf dem Train-Set trainiert (mit Cross-Validation getunet), auf dem Test-Set per RMSE evaluiert, und liefert schließlich Top-10-Filmempfehlungen pro User — gejoint mit `movies.csv` für lesbare Titel.

---

## Export als PNG (für die Doku)

**Option A — Online (am einfachsten):**
1. Mermaid-Code oben kopieren
2. Auf https://mermaid.live einfügen
3. Rechts oben "Actions" → "PNG" oder "SVG" herunterladen
4. Speichern als `results/figures/architektur.png`

**Option B — Lokal per CLI:**
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i docs/architektur.md -o results/figures/architektur.png -w 1600
```

**Option C — VS Code:** Extension "Markdown Preview Mermaid Support" installieren, dann Preview öffnen und Screenshot machen.
