## 1.Run, application_1757606974938_0001, Baseline Run WebGoogle(Kryo)
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/web-Google.txt gs://spark-memory-opt-bucket/out/cc/web-google  
```

## 2.Run, application_1757606974938_0002,WebGoogle (JavaSerializer)
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/ccjob-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.JavaSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/web-Google.txt gs://spark-memory-opt-bucket/out/cc/web-google-java

```

## 3.Run, application_1757697248887_0001, Baseline Run (Kryo) SOC
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
    --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/soc-Live
```

## 4. Run,application_1757697248887_0002, Baseline SOC mit JavaSerializer
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.JavaSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/soc-Live
```