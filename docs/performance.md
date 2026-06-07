# 4.5 Performance-Messung der Datenpipeline

## Ziel der Messung

- **Funktionale Verifikation**: Pipeline läuft sauber auf dem 25M-Datensatz durch.
- **Konfigurations-Check**: Die gewählten Spark-Parameter (driver-memory, partitions) funktionieren auf der 8-GB-VM.
- **Skalierungs-Vergleich**: Wie verhält sich die Laufzeit zwischen Small-Datensatz (lokal) und 25M (VM)?

## Methodik

- Vollständiger Pipeline-Durchlauf je Umgebung: Einlesen → Bereinigung → Train/Test-Split.
- Zeitmessung mit `time.time()` um jede Spark-Aktion (`count`, `randomSplit`).
- Wall-Clock-Zeit, keine Wiederholungen, kein Spark-Profiler.

**Einschränkungen**:
- Nur Einzelmessungen, keine Mittelwerte über mehrere Läufe.
- Dateisystem-Cache des OS nicht kontrolliert — erster Lauf nach Reboot kann langsamer sein.
- Spark-Lazy-Evaluation: `count`-Zeiten enthalten immer die Kosten aller vorgelagerten Transformationen.

Für den Zweck (Größenordnung + Vergleich) ist die Methodik ausreichend.

## Umgebungen

| Parameter         | Lokal (Mac)                   | VM (Ubuntu)                       |
|-------------------|-------------------------------|-----------------------------------|
| Hardware          | MacBook Air (Apple-Silicon)   | 4 vCPUs, 8 GB RAM (virtualisiert) |
| Betriebssystem    | macOS 25.3                    | Ubuntu 24.04 LTS                  |
| Python            | 3.11.10 (via pyenv)           | 3.12.3 (Distributions-Python)     |
| Java              | OpenJDK 17.0.19               | OpenJDK 17.0.19                   |
| PySpark           | 3.5.0                         | 3.5.0                             |
| Datensatz         | MovieLens-Small (100.836)     | MovieLens 25M (25.000.095)        |

## Spark-Konfiguration

| Parameter                       | Lokal | VM   | Begründung                                            |
|---------------------------------|-------|------|-------------------------------------------------------|
| `spark.driver.memory`           | 4g    | 6g   | VM-Wert lässt 2 GB RAM für OS und Hilfsprozesse       |
| `spark.driver.maxResultSize`    | 1g    | 2g   | 25M-Aggregate brauchen mehr als der 1g-Default        |
| `spark.sql.shuffle.partitions`  | 50    | 100  | 100 verteilt Shuffle-Last gut auf 4 vCPUs             |

## Ergebnisse

### Lokal — MovieLens-Small (100.836 Bewertungen)

| Schritt                          | Zeilen                  | Laufzeit (s) |
|----------------------------------|-------------------------|--------------:|
| Einlesen + `count`               | 100.836                 |          5,7  |
| Bereinigung + `count`            | 100.836 (entfernt 0)    |          1,0  |
| Train/Test-Split + 2× `count`    | 80.578 / 20.258         |          1,6  |
| **Gesamt**                       | —                       |        **8,2**|

### VM — MovieLens 25M (25.000.095 Bewertungen)

| Schritt                          | Zeilen                            | Laufzeit (s) |
|----------------------------------|-----------------------------------|--------------:|
| Einlesen + `count`               | 25.000.095                        |         20,0  |
| Bereinigung + `count`            | 25.000.095 (entfernt 0)           |         23,8  |
| Train/Test-Split + 2× `count`    | 19.998.878 / 5.001.217            |         51,5  |
| **Gesamt**                       | —                                 |       **95,4**|

## Beobachtungen

- **Sub-lineare Skalierung**: Datensatz ist 248× größer, Laufzeit nur 11,6× länger.
  - Fixkosten (JVM-Start, Spark-Initialisierung) dominieren bei kleinen Datensätzen.
  - Spark nutzt alle 4 vCPUs aus — ohne Parallelisierung wäre eine ~250× längere Laufzeit zu erwarten gewesen.
- **Engpass auf VM**: Train/Test-Split (51,5 s von 95,4 s).
  - Ursache: Die zwei `count`-Aufrufe nach dem Split lösen jeweils einen vollständigen Spark-Job aus (Lazy Evaluation), der die gesamte Transformations­kette neu berechnet.
  - **Mögliche Optimierung**: `df.cache()` vor dem Split, sodass nachfolgende `count`-Aufrufe aus dem Cache lesen. Auf 8 GB RAM mit 25M Zeilen aber Vorsicht — kann OOM auslösen. Wird im Trainings­schritt (Kapitel 4.3) gezielt eingesetzt.
- **Datenqualität**: `dropna` und `dropDuplicates` entfernen auf beiden Datensätzen 0 Zeilen → MovieLens ist sauber [Harper & Konstan 2015].
- **WARN NativeCodeLoader**: Erscheint einmalig auf der VM (`Unable to load native-hadoop library`). Funktional irrelevant — Spark fällt auf Java-Implementierungen zurück. Performance-Differenz typischerweise <5 %.

## Reproduzierbarkeit

```bash
# Lokal (Mac, Small-Datensatz)
python src/pipeline.py

# VM (25M-Datensatz, getunte Config)
python src/pipeline.py \
    --ratings ~/data/ml-25m/ratings.csv \
    --driver-memory 6g \
    --max-result-size 2g \
    --shuffle-partitions 100
```

## Zusammenfassung

Die Pipeline läuft auf beiden Umgebungen sauber durch. Auf der VM verarbeitet sie den 25M-Datensatz in **95,4 Sekunden** und nutzt dabei alle 4 vCPUs effektiv aus (sub-lineare Skalierung gegenüber Small-Datensatz). Engpass ist der Train/Test-Split wegen Spark-Lazy-Evaluation; eine Cache-Optimierung wäre möglich, ist aber auf 8 GB RAM riskant und wird beim eigentlichen Modelltraining gezielter eingesetzt. Die gewählte Spark-Konfiguration (6g Driver-Memory, 100 Shuffle-Partitionen) ist für die VM passend dimensioniert.

---

**Quellen:** siehe [`docs/literatur.md`](literatur.md)
**KI-Hinweis:** siehe [`docs/ki-nutzung.md`](ki-nutzung.md)
