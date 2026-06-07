# Movie Recommender — DHBW Projekt 8

Collaborative-Filtering-Empfehlungssystem mit **Spark MLlib (ALS)** auf dem **MovieLens 25M**-Datensatz.

**Team:** Nico Baumann, Marco Weber, Lavinia Lauer

## Stack

- Python 3.11 (lokal) / 3.12 (VM)
- PySpark 3.5.0
- Java 17 (für Spark)
- Pandas, Matplotlib, Jupyter

## Repo-Struktur

```
movie-recommender/
├── data/               # NICHT im Repo — separat herunterladen
│   ├── small/          # MovieLens-Small (100k) — für lokale Entwicklung
│   └── ml-25m/         # MovieLens 25M — auf VM
├── docs/               # Dokumentation (Kapitel 2.4, 3.3, 4.1, 4.2, 4.5)
├── src/
│   └── pipeline.py     # Spark-Pipeline (Einlesen, Bereinigung, Train/Test-Split)
└── README.md
```

---

## Setup auf der VM (Erstinstallation)

> Die VM hat `group6@ubuntu` mit `sudo`-Rechten und 8 GB RAM. SSH-Zugang läuft am besten über **VSCode Remote-SSH**.

**1. System & Pakete:**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y openjdk-17-jdk python3-pip python3-venv git unzip wget
```

**2. Virtuelle Umgebung & Python-Pakete:**

```bash
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install --upgrade pip
pip install pyspark==3.5.0 pandas matplotlib jupyter
```

**3. MovieLens-25M-Datensatz herunterladen:**

```bash
mkdir -p ~/data && cd ~/data
wget https://files.grouplens.org/datasets/movielens/ml-25m.zip
unzip ml-25m.zip
```

→ Daten landen unter `~/data/ml-25m/` (außerhalb des Repos).

**4. Repo clonen:**

```bash
cd ~
git clone https://github.com/Nicobaumann21/Meene.git movie-recommender
cd movie-recommender
```

Beim ersten Clone wird nach Login gefragt:
- **Username**: dein GitHub-Username
- **Passwort**: ein Personal Access Token (PAT), erzeugt unter https://github.com/settings/tokens, Scope `repo`

Damit der Token nicht ständig neu eingegeben werden muss:

```bash
git config --global credential.helper store
```

**5. Smoke-Test (Pipeline auf 25M):**

```bash
source ~/venv/bin/activate
cd ~/movie-recommender
python src/pipeline.py \
    --ratings ~/data/ml-25m/ratings.csv \
    --driver-memory 6g \
    --max-result-size 2g \
    --shuffle-partitions 100
```

Erwartete Ausgabe (am Ende): `Train: 19.998.878 | Test: 5.001.217`, Gesamtlaufzeit ca. 80–110 s.

Wenn das durchläuft, ist die VM einsatzbereit. **Ausführliche Setup-Doku:** [`docs/4.1-setup.md`](docs/4.1-setup.md)

---

## Tägliche Arbeit auf der VM

```bash
# Aktuellen Stand vom Repo holen
cd ~/movie-recommender
git pull

# Virtuelle Umgebung aktivieren (in jeder neuen Shell!)
source ~/venv/bin/activate

# Pipeline laufen lassen
python src/pipeline.py --ratings ~/data/ml-25m/ratings.csv \
    --driver-memory 6g --max-result-size 2g --shuffle-partitions 100
```

**Jupyter Notebook mit Port-Forwarding starten** (für interaktives Arbeiten):

```bash
# Auf der VM:
jupyter notebook --no-browser --port=8888

# Auf dem Mac (neues Terminal):
ssh -L 8888:localhost:8888 group6@<vm-host>
```

Anschließend die Token-URL von Jupyter im lokalen Browser öffnen.

---

## Worauf ihr achten müsst

### RAM-Limit (8 GB)
Die VM ist knapp dimensioniert. Wenn ihr Spark-Code schreibt:
- **Spark-Konfiguration nicht weiter aufdrehen** als bei den oben gezeigten Werten (6g Driver, 2g maxResult, 100 Partitionen). Wer mehr will, riskiert OOM.
- **`df.cache()` mit Bedacht einsetzen** — bei 25M Zeilen kann der Cache schnell zum Engpass werden. Nur cachen, was wirklich mehrfach genutzt wird.
- **`toPandas()` auf großen DataFrames vermeiden** — zieht alles in den Driver-RAM. Erst aggregieren/filtern, dann konvertieren.

### Datensätze nicht ins Repo committen
`.gitignore` hat die `data/`-Pfade schon drin. Achtet trotzdem darauf, keine CSVs aus Versehen mit `git add .` zu adden.

### venv-Aktivierung
`source ~/venv/bin/activate` muss in **jeder neuen Shell** wiederholt werden. Erkennbar am `(venv)`-Präfix im Prompt. Sonst landen pip-Installs im System-Python und brechen das Setup.

### Lange Spark-Operationen
Der erste Spark-Start dauert ~20–40 Sekunden (JVM-Hochfahren). Nicht ungeduldig abbrechen.

### Git-Workflow
- Arbeitet auf eigenen Branches: `git checkout -b feature/als-training`
- Push: `git push -u origin feature/als-training`
- Auf GitHub Pull Request, dann Merge in `main`
- Direkt auf `main` pushen vermeiden, damit nichts überschrieben wird

---

## Wer macht was

| Person | Aufgaben | Status |
|--------|----------|--------|
| **Nico (A)** | Infrastruktur, Datenpipeline, VM-Setup | ✅ Fertig |
| **Marco / Lavinia (B/C)** | ALS-Training (4.3), Top-N-Empfehlungen (4.4), Evaluation & Tuning (4.5), Visualisierung (4.6) | Offen |

Die Pipeline (`src/pipeline.py`) liefert bereits sauber bereinigte `train`- und `test`-DataFrames, die ihr direkt für ALS verwenden könnt.

---

## Dokumentation

Die ausführliche Doku liegt in [`docs/`](docs/):

- [`2.4-datensatz.md`](docs/2.4-datensatz.md) — MovieLens 25M (Inhalt, Kennzahlen)
- [`3.3-tech-stack.md`](docs/3.3-tech-stack.md) — Technologie-Stack & Begründung
- [`4.1-setup.md`](docs/4.1-setup.md) — VM-Setup Schritt für Schritt
- [`4.2-datenvorverarbeitung.md`](docs/4.2-datenvorverarbeitung.md) — Pipeline-Bereinigung
- [`performance.md`](docs/performance.md) — Laufzeitmessungen (Kapitel 4.5)
- [`literatur.md`](docs/literatur.md) — Quellen
- [`ki-nutzung.md`](docs/ki-nutzung.md) — KI-Nutzungs-Hinweis
