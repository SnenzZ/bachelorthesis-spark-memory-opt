import json, os, pandas as pd
from collections import defaultdict

LOG_PATH = "spark_logs/spark-history_application_1755180100477_0001"
OUT_DIR = "results"
os.makedirs(OUT_DIR, exist_ok=True)

# --- 1) zeilenweise parsen (streaming, robust) ---
stages_rows = []
stage_names = {}  # (stageId, attemptId) -> name
spark_props = {}

with open(LOG_PATH, "r") as f:
    for line in f:
        e = json.loads(line)

        # Konfiguration einsammeln (einmal)
        if e.get("Event") == "SparkListenerEnvironmentUpdate" and not spark_props:
            spark_props = e.get("Spark Properties", {})

        # Stage-Namen (mit Attempt)
        if e.get("Event") == "SparkListenerStageCompleted":
            si = e.get("Stage Info", {}) or {}
            sid = si.get("Stage ID")
            att = si.get("Stage Attempt ID", 0)
            stage_names[(sid, att)] = si.get("Stage Name")

        # Task-Metriken
        if e.get("Event") == "SparkListenerTaskEnd":
            sid = e.get("Stage ID")
            att = e.get("Stage Attempt ID", 0)
            m = e.get("Task Metrics", {}) or {}
            sr = m.get("Shuffle Read Metrics", {}) or {}
            sw = m.get("Shuffle Write Metrics", {}) or {}

            stages_rows.append({
                "stage_id": sid,
                "stage_attempt_id": att,
                "executor_run_time_ms": m.get("Executor Run Time", 0),
                "gc_time_ms": m.get("JVM GC Time", 0),
                "shuffle_read_mb": (
                    sr.get("Local Bytes Read", 0)
                    + sr.get("Remote Bytes Read", 0)
                    + sr.get("Remote Bytes Read To Disk", 0)
                ) / 1e6,
                "shuffle_write_mb": sw.get("Shuffle Bytes Written", 0) / 1e6,
                "spill_mb": (
                    m.get("Memory Bytes Spilled", 0)
                    + m.get("Disk Bytes Spilled", 0)
                ) / 1e6,
                "task_failed": 1 if e.get("Task End Reason", {}).get("Reason") != "Success" else 0
            })

# --- 2) Aggregation pro (Stage, Attempt) ---
df_tasks = pd.DataFrame(stages_rows)
if df_tasks.empty:
    raise SystemExit("Keine Task-Metriken gefunden. Prüfe LOG_PATH oder ob Event-Logging aktiv war.")

stage_summary = (
    df_tasks.groupby(["stage_id","stage_attempt_id"], as_index=False)
            .sum(numeric_only=True)
)

# Namen mappen
stage_summary["stage_name"] = stage_summary.apply(
    lambda r: stage_names.get((r["stage_id"], r["stage_attempt_id"])), axis=1
)

# Optional: Config-Spalten anreichern
for k in ["spark.executor.instances", "spark.executor.cores",
          "spark.executor.memory", "spark.executor.memoryOverhead",
          "spark.default.parallelism", "spark.serializer",
          "spark.memory.fraction", "spark.shuffle.compress"]:
    stage_summary[k.replace(".", "_")] = spark_props.get(k)

# Reihenfolge der Spalten
cols = ["stage_id","stage_attempt_id","stage_name",
        "executor_run_time_ms","gc_time_ms",
        "shuffle_read_mb","shuffle_write_mb","spill_mb",
        "task_failed",
        "spark_executor_instances","spark_executor_cores",
        "spark_executor_memory","spark_executor_memoryOverhead",
        "spark_default_parallelism","spark_serializer",
        "spark_memory_fraction","spark_shuffle_compress"]
stage_summary = stage_summary[cols]

# --- 3) Spaltennamen vereinheitlichen (klein + underscore) ---
stage_summary.columns = (
    stage_summary.columns.str.lower()
                          .str.replace(" ", "_")
)

# --- 4) Export ---
out_csv = os.path.join(OUT_DIR, "stage_metrics.csv")
stage_summary.to_csv(out_csv, index=False)
print(f"CSV gespeichert unter: {out_csv}")
