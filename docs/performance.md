# 4.5 Performance-Messung der Datenpipeline

## 4.5.1 Zielsetzung und methodisches Vorgehen

Im Rahmen der Lösungs­beschreibung wird die Pipeline aus Kapitel 4.2 systematisch auf beiden eingesetzten Umgebungen vermessen. Ziel ist es,

1. die **funktionale Korrektheit** der Pipeline auf dem realistisch dimensionierten Datensatz (MovieLens 25M) zu belegen,
2. die **Wirksamkeit** der gewählten Spark-Konfiguration (Treiberspeicher, Partitionierung) zu prüfen und
3. das **Skalierungs­verhalten** zwischen kleinem Entwicklungs- und großem Produktions­datensatz quantitativ zu charakterisieren.

Die Messungen erfolgen jeweils als Durchlauf der vollständigen Pipeline (Einlesen → Bereinigung → Train/Test-Split). Innerhalb der Pipeline werden die Zeitdauern der einzelnen Spark-Aktionen mit `time.time()` umschlossen und auf Konsolen­ausgabe geschrieben. Bewusst wird dabei nicht der Spark-eigene Web-UI-basierte Profiler genutzt, sondern eine einfache Wall-Clock-Messung — dies ist für die hier verfolgte Aussage (Größenordnung und Vergleich) hinreichend und vermeidet zusätzliche Abhängigkeiten.

**Caveats der Messmethode:**

- Es werden keine wiederholten Läufe und keine Mittelwerte gebildet. Die Werte sind als Einzelmessungen zu verstehen.
- Cache-Effekte des Betriebssystems (Dateisystem-Cache) sind nicht kontrolliert; der erste Lauf nach einem Neustart der VM kann langsamer ausfallen.
- Die Spark-eigene Lazy Evaluation führt dazu, dass die Laufzeit einer scheinbar einfachen Operation wie `count()` immer auch die Kosten aller zuvor definierten Transformationen enthält.

Trotz dieser Einschränkungen erlauben die Ergebnisse belastbare qualitative Aussagen über das Verhalten des Systems.

## 4.5.2 Eingesetzte Umgebungen

| Parameter         | Lokale Umgebung (Mac)        | Ziel-VM (Ubuntu)                  |
|-------------------|------------------------------|-----------------------------------|
| Hardware          | MacBook Air (Apple-Silicon)  | 4 vCPUs, 8 GB RAM, Virt-Hypervisor|
| Betriebssystem    | macOS 25.3 (Darwin 25.3.0)   | Ubuntu 24.04 LTS                  |
| Python            | 3.11.10 (via `pyenv`)        | 3.12.3 (Distributions-Python)     |
| Java              | OpenJDK 17.0.19 (Homebrew)   | OpenJDK 17.0.19 (Distributionspaket)|
| PySpark           | 3.5.0                        | 3.5.0                             |
| Datensatz         | MovieLens-Small (100.836 Zeilen) | MovieLens 25M (25.000.095 Zeilen) |
| Datenpfad         | `data/small/ratings.csv` (Repo) | `~/data/ml-25m/ratings.csv` (außerhalb Repo) |

## 4.5.3 Spark-Konfiguration

Die für die Messungen verwendeten Spark-Konfigurations­parameter sind unten zusammengefasst. Die Werte für die VM stützen sich auf die Empfehlungen der offiziellen Apache-Spark-Dokumentation [Apache Spark 2024] und auf orientierende Vortests.

| Parameter                       | Lokal | VM   | Begründung                                                |
|---------------------------------|-------|------|-----------------------------------------------------------|
| `spark.driver.memory`           | 4g    | 6g   | VM verfügt über 8 GB RAM; 6 GB für Spark, 2 GB Reserve für OS und Hilfsprozesse |
| `spark.driver.maxResultSize`    | 1g    | 2g   | Zwischen­ergebnisse von Aggregationen auf 25M-Zeilen können den 1 GB-Default überschreiten |
| `spark.sql.shuffle.partitions`  | 50    | 100  | Auf 4 vCPUs verteilen 100 Partitionen die Shuffle-Last besser als der Spark-Default (200) und verursachen weniger Overhead als noch höhere Werte |

Die Anwendung dieser Parameter erfolgt über Kommandozeilen­argumente an `src/pipeline.py` (vgl. Kapitel 4.1.10 und 4.1.12).

## 4.5.4 Messergebnisse

### Lokale Umgebung — MovieLens-Small (100.836 Bewertungen)

| Schritt                          | Zeilen                  | Laufzeit (s) |
|----------------------------------|-------------------------|--------------:|
| Einlesen + `count`               | 100.836                 |          5,7  |
| Bereinigung + `count`            | 100.836 (entfernt 0)    |          1,0  |
| Train/Test-Split + 2× `count`    | 80.578 / 20.258         |          1,6  |
| **Gesamtlaufzeit (Wall-Clock)**  | —                       |        **8,2**|

Bemerkenswert ist hier der hohe Anteil des ersten Schritts (5,7 s) an der Gesamtzeit. Dieser entfällt zum überwiegenden Teil auf den initialen Start der JVM und die Initialisierung des Spark-Contexts; die eigentliche Datei­verarbeitung ist bei 100.836 Zeilen verschwindend gering.

### Ziel-VM — MovieLens 25M (25.000.095 Bewertungen)

| Schritt                          | Zeilen                            | Laufzeit (s) |
|----------------------------------|-----------------------------------|--------------:|
| Einlesen + `count`               | 25.000.095                        |         20,0  |
| Bereinigung + `count`            | 25.000.095 (entfernt 0)           |         23,8  |
| Train/Test-Split + 2× `count`    | 19.998.878 / 5.001.217            |         51,5  |
| **Gesamtlaufzeit (Wall-Clock)**  | —                                 |       **95,4**|

## 4.5.5 Analyse und Diskussion

### Skalierungs­verhalten

Bei einer Vergrößerung des Datensatzes um den Faktor 248 (von 100.836 auf 25.000.095 Zeilen) steigt die Gesamtlaufzeit lediglich um den Faktor 11,6 (von 8,2 s auf 95,4 s). Daraus lassen sich zwei Schlüsse ziehen:

1. **Fixkostenanteil**: Ein erheblicher Anteil der Laufzeit kleiner Datensätze besteht aus festen Aufwänden (JVM-Start, Spark-Initialisierung, Schemainferenz). Diese werden bei steigender Datenmenge nicht größer und dominieren bei kleinen Datensätzen die Gesamtzeit.
2. **Sub-lineare Skalierung**: Die parallelisierbaren Bestandteile der Pipeline skalieren effektiv mit der Anzahl verfügbarer CPU-Kerne. Spark nutzt auf der VM alle 4 vCPUs aus; ohne diese Parallelisierung wäre eine annähernd lineare Skalierung (Faktor ~250) zu erwarten gewesen.

### Engpass-Identifikation

Auf der VM dominiert der **Train/Test-Split mit 51,5 s** die Gesamtlaufzeit. Die Ursache liegt darin, dass die anschließenden zwei `count`-Operationen (`train.count()` und `test.count()`) jeweils einen vollständigen Spark-Job auslösen, der die gesamte Transformations­kette von der CSV-Datei bis zum Split neu berechnet. Dieses Verhalten ist auf Sparks **Lazy Evaluation** zurückzuführen: Transformationen wie `randomSplit` werden erst beim Aufruf einer Action (z. B. `count`) tatsächlich ausgeführt.

Eine potenzielle Optimierung wäre das **Cachen des bereinigten DataFrames** vor dem Split:

```python
df = clean(df_raw).cache()
df.count()  # materialisiert den Cache
train, test = df.randomSplit([0.8, 0.2], seed=42)
```

Damit würden `train.count()` und `test.count()` aus dem Spark-internen Cache lesen, statt die CSV erneut zu parsen. Allerdings ist Caching auf einer 8-GB-VM nur mit Bedacht einzusetzen — bei 25 Millionen Zeilen wird der Cache schnell zum Engpass und kann Out-of-Memory-Fehler auslösen. Im Rahmen der reinen Pipeline­ausführung wurde auf den Cache verzichtet, weil die `count`-Aufrufe vorrangig der Verifikation dienen; im späteren Trainingsschritt (Kapitel 4.3) wird `cache()` selektiv eingesetzt werden.

### Qualität der Daten

Auf beiden Datensätzen entfernten die Bereinigungs­schritte (`dropna`, `dropDuplicates`) **keine einzige Zeile**. Dies bestätigt empirisch die hohe Vorabqualität der MovieLens-Daten, wie sie auch von Harper & Konstan [2015] beschrieben wird. Die Bereinigungs­schritte bleiben dennoch im Code, da sie als robustes Sicherheits­netz gegen Datenfehler in zukünftigen Releases des Datensatzes dienen.

### Beobachtete Warnungen

Auf der VM erscheint einmalig die Warnung:

```
WARN NativeCodeLoader: Unable to load native-hadoop library for your platform...
using builtin-java classes where applicable
```

Diese Meldung tritt regelmäßig in Spark-Installationen ohne kompilierte Hadoop-Native-Bibliotheken auf. Sie ist **funktional ohne Konsequenz**, da Spark in diesem Fall auf reine Java-Implementierungen zurückfällt. Der Performance-Unterschied ist in den hier durchgeführten Messungen nicht beobachtbar und liegt in der Literatur typischerweise unter 5 %.

## 4.5.6 Reproduzierbarkeit

Sämtliche Messungen lassen sich mit folgenden Befehlen reproduzieren (vorausgesetzt, die in Kapitel 4.1 beschriebene Umgebung wurde eingerichtet):

```bash
# Lokale Umgebung (MovieLens-Small, Standardparameter)
python src/pipeline.py

# Ziel-VM (MovieLens 25M, getunte Konfiguration)
python src/pipeline.py \
    --ratings ~/data/ml-25m/ratings.csv \
    --driver-memory 6g \
    --max-result-size 2g \
    --shuffle-partitions 100
```

Die Ausgabe der Pipeline enthält in jedem Lauf die hier dargestellten Kennzahlen, sodass Vergleichs­messungen — etwa nach einem späteren Hardware-Wechsel oder einem Spark-Update — unmittelbar möglich sind.

---

*Verwendete Literatur: siehe [docs/literatur.md](literatur.md).*
