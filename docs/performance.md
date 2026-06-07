# Performance-Messung

Laufzeiten der Datenpipeline (`src/pipeline.py`) auf den beiden eingesetzten Umgebungen. Gemessen wird mit `time.time()` um die einzelnen Spark-Aktionen herum.

## Umgebungen

| Parameter         | Lokal (Mac)             | VM (Ubuntu)                  |
|-------------------|-------------------------|------------------------------|
| Hardware          | MacBook Air (M-Chip)    | 4 vCPUs, 8 GB RAM            |
| OS                | macOS 25.3              | Ubuntu 24.04                 |
| Python            | 3.11.10                 | 3.12.3                       |
| Java              | OpenJDK 17.0.19         | OpenJDK 17.0.19              |
| PySpark           | 3.5.0                   | 3.5.0                        |
| Datensatz         | MovieLens-Small (100k)  | MovieLens 25M (25.000.095)   |

## Spark-Konfiguration

| Parameter                       | Lokal | VM   | Begründung                                              |
|---------------------------------|-------|------|---------------------------------------------------------|
| `spark.driver.memory`           | 4g    | 6g   | VM hat 8 GB RAM — 6g für Driver, 2g Reserve für OS      |
| `spark.driver.maxResultSize`    | 1g    | 2g   | Zwischenergebnisse bei 25M-Aggregationen größer         |
| `spark.sql.shuffle.partitions`  | 50    | 100  | Mehr Partitionen verteilen Shuffle-Last besser auf 4 vCPUs |

## Messergebnisse

### Lokal — MovieLens-Small (100.836 Bewertungen)

| Schritt                      | Zeilen      | Laufzeit |
|------------------------------|------------:|---------:|
| Einlesen + `count`           | 100.836     | 5.7s     |
| Bereinigung + `count`        | 100.836     | 1.0s     |
| Train/Test-Split + 2× `count`| 80.578 / 20.258 | 1.6s |
| **Gesamt**                   |             | **8.2s** |

### VM — MovieLens 25M (25.000.095 Bewertungen)

| Schritt                      | Zeilen          | Laufzeit |
|------------------------------|----------------:|---------:|
| Einlesen + `count`           | 25.000.095      | 20.0s    |
| Bereinigung + `count`        | 25.000.095      | 23.8s    |
| Train/Test-Split + 2× `count`| 19.998.878 / 5.001.217 | 51.5s |
| **Gesamt**                   |                 | **95.4s**|

## Beobachtungen

- **Skalierungsverhalten**: Der Datensatz ist ~248× größer, die Pipeline läuft aber nur ~12× länger. Spark profitiert hier deutlich von paralleler Ausführung und der gewählten Partitionierung.
- **Sauberkeit der Daten**: 0 Zeilen wurden bei `dropna()`/`dropDuplicates()` entfernt — der MovieLens-Datensatz ist bereits aufbereitet.
- **Engpass auf der VM**: Der Train/Test-Split dominiert die Laufzeit (51.5s von 95.4s), weil Spark hier zwei `count`-Aktionen über den gesamten Datensatz auslöst. Für reines Training wäre das Caching nach `clean()` (`df.cache()`) eine Option, wenn der Speicher es zulässt.
- **Warnung**: Auf der VM erscheint einmalig `WARN NativeCodeLoader: Unable to load native-hadoop library` — funktional irrelevant (Spark fällt auf Java-Implementierungen zurück), aber dokumentiert.

## Reproduzierbarkeit

```bash
# Lokal (Mac)
python src/pipeline.py

# VM (25M-Datensatz)
python src/pipeline.py \
    --ratings ~/data/ml-25m/ratings.csv \
    --driver-memory 6g \
    --max-result-size 2g \
    --shuffle-partitions 100
```
