import json, pandas as pd
from collections import defaultdict

# Eventlog (NDJSON) zeilenweise einlesen
with open("spark_logs/spark-history_application_1755180100477_0001") as f:
    events = [json.loads(line) for line in f]

rows = []
for e in events:
    if e.get("Event") == "SparkListenerTaskEnd":
        stg = e["Stage ID"]
        metrics = e.get("Task Metrics", {}) or {}

        sr = metrics.get("Shuffle Read Metrics", {}) or {}
        sw = metrics.get("Shuffle Write Metrics", {}) or {}

        row = {
            "Stage ID": stg,
            "Executor Run Time (ms)": metrics.get("Executor Run Time", 0),
            "GC Time (ms)": metrics.get("JVM GC Time", 0),
            # Shuffle READ: lokale + Remote-Bytes addieren
            "Shuffle Read (MB)": (
                sr.get("Local Bytes Read", 0)
                + sr.get("Remote Bytes Read", 0)
                + sr.get("Remote Bytes Read To Disk", 0)
            ) / 1e6,
            # Shuffle WRITE
            "Shuffle Write (MB)": sw.get("Shuffle Bytes Written", 0) / 1e6,
            # Spill (Memory + Disk)
            "Spill (MB)": (
                metrics.get("Memory Bytes Spilled", 0)
                + metrics.get("Disk Bytes Spilled", 0)
            ) / 1e6,
        }
        rows.append(row)

df_tasks = pd.DataFrame(rows)

# → pro Stage aggregieren (Summe ist bei diesen Bytes üblich)
stage_summary = df_tasks.groupby("Stage ID", as_index=False).sum(numeric_only=True)

# Optional: Stage-Namen ergänzen (aus StageCompleted)
stage_names = {}
for e in events:
    if e.get("Event") == "SparkListenerStageCompleted":
        si = e.get("Stage Info", {})
        stage_names[si.get("Stage ID")] = si.get("Stage Name")

stage_summary["Stage Name"] = stage_summary["Stage ID"].map(stage_names)
stage_summary = stage_summary[
    ["Stage ID","Stage Name","Executor Run Time (ms)","GC Time (ms)",
     "Shuffle Read (MB)","Shuffle Write (MB)","Spill (MB)"]
]
print(stage_summary.head())
# Ergebnis in eine CSV-Datei schreiben
output_path = "results/stage_metrics.csv"   # Pfad anpassen, Ordner vorher anlegen
stage_summary.to_csv(output_path, index=False)

print(f"CSV gespeichert unter: {output_path}")
