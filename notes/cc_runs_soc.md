1) Baseline Config mit Kryo - H1, 	application_1758971495964_0001, application_1758971495964_0002, application_1758971495964_0003, application_1758971495964_0004	
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/soc-Live

```

2) Java Serializer - H1, application_1758971495964_0005, application_1758971495964_0006, application_1758971495964_0007, application_1758971495964_0009
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.JavaSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/soc-Live-java
```