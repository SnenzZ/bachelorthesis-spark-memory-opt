# Bachelorarbeit – Spark Memory Optimization for Graph Workloads

Dieses Repository enthält den Quellcode und experimentelle Ergebnisse meiner Bachelorarbeit mit dem Titel:

**„Optimizing Apache Spark Memory Configuration for Efficient Execution of Graph Workloads“**

Ziel der Arbeit ist es, das Speicherverhalten von Graph-Algorithmen (z. B. PageRank, Connected Components) in Apache Spark (GraphX) zu analysieren und Optimierungspotenziale bei verschiedenen Speicherparametern aufzudecken.

---

## 📁 Projektstruktur

```
.
├── Main.scala   # Hauptprogramm zum Ausführen von Graph-Algorithmen
├── build.sbt                    # Scala-Build-Konfiguration
├── data/                        # Beispieldatensätze (z. B. web-Google.txt)
├── results/                     # Logs, Output-Daten und Diagramme
├── scripts/                     # Bash- oder Python-Skripte zur Automatisierung
└── README.md                    # Diese Datei
```

---

## 🚀 Schnellstart

### Voraussetzungen

- Java 8 oder 11
- Scala 2.12.x
- sbt (Scala Build Tool)
- Apache Spark 3.x

### Lokales Ausführen

```bash
sbt run
```

Mit Parametern (Dateipfad + Algorithmus):

```bash
sbt "run web-Google.txt pagerank"
```

Dies lädt die Datei `web-Google.txt` als Kantenliste und startet z. B. PageRank.

---

## 📊 Forschungsfokus

- **Speicherverhalten** unter verschiedenen Spark-Konfigurationen:
    - `spark.memory.fraction`
    - `executor.memory`
    - `storageLevel` (z. B. MEMORY_ONLY vs. MEMORY_AND_DISK)
- **Graphcharakteristika**, die Speicherbedarf beeinflussen (z. B. Knotenzahl, Gradverteilung)
- **Laufzeit- und GC-Analysen**

Tests erfolgen lokal und auf dem Cluster auf der Google Cloud Platform.

---


## 👤 Autor

**Nguyen Duc Rohr**  
TU Berlin – Bachelorarbeit DOS, 2025  
[GitHub @SnenzZ](https://github.com/SnenzZ)

