import json, os, pandas as pd
from collections import defaultdict

LOG_PATH = "spark_logs/spark-history_application_1755180100477_0001"
OUT_DIR = "results"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Helpers ---
def to_mb(x_bytes): return x_bytes / 1e6

def first_non_null(*vals):
    for v in vals:
        if v not in (None, 0):
            return v
    return 0

# --- Stores ---
spark_props = {}
exec_info = {}       # exec_id -> {host, total_cores, add_time, remove_time, ...}
host_to_execs = defaultdict(set)  # host -> {exec_ids}
exec_mem_caps = {}  # exec_id -> {max_onheap_bytes, max_offheap_bytes}
agg = defaultdict(lambda: defaultdict(float))        # per-exec numeric metrics
task_counts = defaultdict(lambda: {"tasks_total": 0, "tasks_failed": 0})

# Debug-Zähler
n_taskend = 0
n_taskend_no_exec = 0
n_taskend_resolved_via_host = 0

with open(LOG_PATH, "r") as f:
    for line in f:
        e = json.loads(line)
        ev = e.get("Event")

        # Spark Properties
        if ev == "SparkListenerEnvironmentUpdate" and not spark_props:
            spark_props = e.get("Spark Properties", {}) or {}

        # Executor Added/Removed
        elif ev == "SparkListenerExecutorAdded":
            exec_id = e.get("Executor ID")
            info = e.get("Executor Info", {}) or {}
            host = info.get("Host") or info.get("Executor Host")
            exec_info.setdefault(exec_id, {})
            exec_info[exec_id].update({
                "host": host,
                "total_cores": info.get("Total Cores"),
                "resource_profile_id": e.get("Resource Profile Id"),
                "log_urls": info.get("Log Urls"),
                "add_time": e.get("Timestamp"),
            })
            if host and exec_id:
                host_to_execs[host].add(exec_id)

        elif ev == "SparkListenerExecutorRemoved":
            exec_id = e.get("Executor ID")
            if exec_id:
                exec_info.setdefault(exec_id, {})
                exec_info[exec_id]["remove_time"] = e.get("Timestamp")

        # BlockManager Added -> Kapazitäten
        elif ev == "SparkListenerBlockManagerAdded":
            bm = e.get("Block Manager", {}) or {}
            exec_id = bm.get("Executor ID")
            if exec_id:
                exec_mem_caps[exec_id] = {
                    "max_onheap_bytes": bm.get("Maximum OnHeap Memory", 0),
                    "max_offheap_bytes": bm.get("Maximum OffHeap Memory", 0),
                }

        # TaskEnd -> per-executor Metriken
        elif ev == "SparkListenerTaskEnd":
            n_taskend += 1
            ti = e.get("Task Info", {}) or {}
            # Richtige Quelle: Task Info -> Executor ID
            exec_id = ti.get("Executor ID")
            host = ti.get("Host")

            if not exec_id:
                # Fallback: über Host auflösen (sofern genau ein Executor auf dem Host)
                cand = list(host_to_execs.get(host, []))
                if len(cand) == 1:
                    exec_id = cand[0]
                    n_taskend_resolved_via_host += 1

            if not exec_id:
                n_taskend_no_exec += 1
                continue  # ohne Executor-ID nicht aggregierbar

            # Task-Status
            task_counts[exec_id]["tasks_total"] += 1
            reason = e.get("Task End Reason", {}) or {}
            if reason.get("Reason") != "Success":
                task_counts[exec_id]["tasks_failed"] += 1

            m = e.get("Task Metrics", {}) or {}
            sr = m.get("Shuffle Read Metrics", {}) or {}
            sw = m.get("Shuffle Write Metrics", {}) or {}

            agg[exec_id]["executor_run_time_ms"] += m.get("Executor Run Time", 0)
            agg[exec_id]["jvm_gc_time_ms"] += m.get("JVM GC Time", 0)

            # Shuffle Read = local + remote + remote_to_disk
            remote_to_disk = first_non_null(
                sr.get("Remote Bytes Read To Disk", 0),
                sr.get("Remote Bytes ReadToDisk", 0)  # falls abweichende Schreibweise
            )
            shuffle_read_bytes = (
                sr.get("Local Bytes Read", 0)
                + sr.get("Remote Bytes Read", 0)
                + remote_to_disk
            )
            agg[exec_id]["shuffle_read_mb"] += shuffle_read_bytes / 1e6

            # Shuffle Write
            agg[exec_id]["shuffle_write_mb"] += sw.get("Shuffle Bytes Written", 0) / 1e6

            # Spills
            agg[exec_id]["memory_spill_mb"] += m.get("Memory Bytes Spilled", 0) / 1e6
            agg[exec_id]["disk_spill_mb"] += m.get("Disk Bytes Spilled", 0) / 1e6

# DataFrame bauen
rows = []
all_exec_ids = set(list(agg.keys()) + list(exec_info.keys()) + list(exec_mem_caps.keys()))

for exec_id in all_exec_ids:
    a = agg.get(exec_id, {})
    info = exec_info.get(exec_id, {})
    caps = exec_mem_caps.get(exec_id, {})

    add_ts = info.get("add_time")
    rm_ts = info.get("remove_time")
    uptime_ms = (rm_ts - add_ts) if (isinstance(add_ts, int) and isinstance(rm_ts, int)) else None

    rows.append({
        "executor_id": exec_id,
        "host": info.get("host"),
        "total_cores": info.get("total_cores"),
        "resource_profile_id": info.get("resource_profile_id"),
        "uptime_ms": uptime_ms,
        "max_onheap_mb": to_mb(caps.get("max_onheap_bytes", 0)),
        "max_offheap_mb": to_mb(caps.get("max_offheap_bytes", 0)),
        "executor_run_time_ms": a.get("executor_run_time_ms", 0.0),
        "jvm_gc_time_ms": a.get("jvm_gc_time_ms", 0.0),
        "shuffle_read_mb": a.get("shuffle_read_mb", 0.0),
        "shuffle_write_mb": a.get("shuffle_write_mb", 0.0),
        "memory_spill_mb": a.get("memory_spill_mb", 0.0),
        "disk_spill_mb": a.get("disk_spill_mb", 0.0),
        "tasks_total": task_counts[exec_id]["tasks_total"],
        "tasks_failed": task_counts[exec_id]["tasks_failed"],
        "spark_executor_instances": spark_props.get("spark.executor.instances"),
        "spark_executor_cores": spark_props.get("spark.executor.cores"),
        "spark_executor_memory": spark_props.get("spark.executor.memory"),
        "spark_executor_memoryOverhead": spark_props.get("spark.executor.memoryOverhead"),
        "spark_default_parallelism": spark_props.get("spark.default.parallelism"),
        "spark_serializer": spark_props.get("spark.serializer"),
        "spark_memory_fraction": spark_props.get("spark.memory.fraction"),
        "spark_shuffle_compress": spark_props.get("spark.shuffle.compress"),
    })

df_exec = pd.DataFrame(rows)
if df_exec.empty:
    raise SystemExit("Keine Executor-Metriken gefunden. Prüfe LOG_PATH/Event-Logging.")

# Spalten normalisieren & sortieren
df_exec.columns = df_exec.columns.str.lower().str.replace(" ", "_")
col_order = [
    "executor_id","host","total_cores","resource_profile_id","uptime_ms",
    "max_onheap_mb","max_offheap_mb",
    "executor_run_time_ms","jvm_gc_time_ms",
    "shuffle_read_mb","shuffle_write_mb",
    "memory_spill_mb","disk_spill_mb",
    "tasks_total","tasks_failed",
    "spark_executor_instances","spark_executor_cores",
    "spark_executor_memory","spark_executor_memoryoverhead",
    "spark_default_parallelism","spark_serializer",
    "spark_memory_fraction","spark_shuffle_compress"
]
df_exec = df_exec[[c for c in col_order if c in df_exec.columns]]

# Export
out_csv = os.path.join(OUT_DIR, "executor_metrics.csv")
df_exec.to_csv(out_csv, index=False)
print(f"CSV gespeichert unter: {out_csv}")

# Kurze Debug-Zusammenfassung
print(f"TaskEnd-Events gesamt: {n_taskend}")
print(f"…davon ohne Executor-ID: {n_taskend_no_exec} (via Host gelöst: {n_taskend_resolved_via_host})")
