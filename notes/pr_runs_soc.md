1) Baseline Config mit Kryo - H1, application_1758976209174_0005, application_1758976209174_0006, application_1758976209174_0007
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=PRJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties="spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history" \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt \
     gs://spark-memory-opt-bucket/out/pr/soc-Live-kryo \
     20 0.15 100

```

2) Java Serializer - H1, application_1758976209174_0004, application_1758976209174_0008, application_1758976209174_0009
```bash
# Java-Serializer
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=PRJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.JavaSerializer,\
spark.eventLog.enabled=true,\
spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt \
     gs://spark-memory-opt-bucket/out/pr/soc-Live-java \
     20 0.15 100

```