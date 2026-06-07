# 4.1 Setup der Entwicklungsumgebung (Ubuntu-VM)

Dieses Dokument beschreibt die vollständige Einrichtung der Ubuntu-VM für das Projekt. Alle Befehle wurden auf einer frischen **Ubuntu 24.04 Desktop**-VM (4 vCPUs, 8 GB RAM, ~50 GB Disk) ausgeführt.

## 4.1.1 Zugriff per SSH

Der Zugriff erfolgt von einem Mac per SSH (mit hinterlegtem öffentlichem Schlüssel auf der VM):

```bash
ssh <user>@<vm-host>
```

Zur Arbeit mit IDE-Komfort wird **VSCode mit der "Remote-SSH"-Extension** genutzt — Editor und Terminal laufen lokal, der Code wird aber direkt auf der VM ausgeführt.

## 4.1.2 System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

Stellt sicher, dass alle Paketquellen und installierten Pakete auf dem neuesten Stand sind.

## 4.1.3 Systempakete installieren

```bash
sudo apt install -y openjdk-17-jdk python3-pip python3-venv git unzip wget
```

| Paket            | Zweck                                              |
|------------------|----------------------------------------------------|
| `openjdk-17-jdk` | Java 17 — Pflicht für Spark (3.5 unterstützt 8/11/17) |
| `python3-pip`    | Paketmanager für Python                            |
| `python3-venv`   | Python-Virtual-Environments                        |
| `git`            | Versionskontrolle (Repo clonen)                    |
| `unzip`, `wget`  | Download und Entpacken von MovieLens 25M           |

Verifikation:

```bash
java -version       # openjdk version "17.x.x"
python3 --version   # Python 3.x.x
git --version
```

## 4.1.4 Virtuelle Python-Umgebung

```bash
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install --upgrade pip
```

Aktivieren bei jeder neuen Shell mit `source ~/venv/bin/activate`. Im aktivierten Prompt steht `(venv)` voran.

## 4.1.5 Python-Pakete installieren

```bash
pip install pyspark==3.5.0 pandas matplotlib jupyter
```

Versionen werden explizit gepinnt, damit lokale und VM-Umgebung identisch sind.

## 4.1.6 MovieLens 25M herunterladen

```bash
mkdir -p ~/data
cd ~/data
wget https://files.grouplens.org/datasets/movielens/ml-25m.zip
unzip ml-25m.zip
ls ml-25m/
```

Erwarteter Inhalt:

| Datei             | Größe   | Bedeutung                                |
|-------------------|---------|------------------------------------------|
| `ratings.csv`     | ~647 MB | 25 Mio. Bewertungen (userId, movieId, rating, timestamp) |
| `movies.csv`      | ~2.9 MB | 62.000 Filme mit Titel und Genre         |
| `tags.csv`        | ~16 MB  | Nutzer-Tags                              |
| `links.csv`       | ~1.4 MB | Verknüpfung mit IMDb/TMDb                |
| `genome-scores.csv`/`genome-tags.csv` | ~370 MB | Tag-Genome (für Content-Based, hier nicht genutzt) |

## 4.1.7 Repository klonen

```bash
cd ~
git clone https://github.com/Nicobaumann21/Meene.git movie-recommender
cd movie-recommender
```

## 4.1.8 Jupyter mit SSH-Port-Forwarding starten

**Auf der VM:**

```bash
source ~/venv/bin/activate
cd ~/movie-recommender
jupyter notebook --no-browser --port=8888
```

Jupyter gibt eine URL mit Token aus, z. B.:
```
http://localhost:8888/?token=abc123...
```

**Auf dem Mac (in neuem Terminal):**

```bash
ssh -L 8888:localhost:8888 <user>@<vm-host>
```

Damit wird Port 8888 der VM auf den lokalen Port 8888 weitergeleitet. Anschließend die URL aus dem Jupyter-Output im Mac-Browser öffnen.

## 4.1.9 Verifikation des Setups

Test-Skript, das prüft, dass Spark sauber startet:

```bash
source ~/venv/bin/activate
cd ~/movie-recommender
python src/pipeline.py
```

Lokal (Mac, MovieLens-Small) sollten ca. 100.836 Zeilen verarbeitet werden, auf der VM mit dem 25M-Datensatz entsprechend 25.000.095 (siehe Kapitel 4.5 für Laufzeiten).
