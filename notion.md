## 1.Run, Baseline Run WebGoogle(Kryo), application_1757606974938_0001
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/web-Google.txt gs://spark-memory-opt-bucket/out/cc/web-google  
```

## 2.Run, WebGoogle (JavaSerializer), application_1757606974938_0002
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/ccjob-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.JavaSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/web-Google.txt gs://spark-memory-opt-bucket/out/cc/web-google-java

```

## 3.Run, Baseline Run (Kryo) SOC, application_1757697248887_0001
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
    --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/soc-Live
```

## 4.Run, Baseline SOC mit JavaSerializer, application_1757697248887_0002
```bash
gcloud dataproc jobs submit spark \
  --cluster=baseline-cluster \
  --region=europe-west3 \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.JavaSerializer,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/soc-Live
```


## 5.Run, 3g / 768m mit SOC, application_1757862796140_0002 
```bash
gcloud dataproc jobs submit spark --cluster=baseline-cluster --region=europe-west3 \
  --class=CCJob --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.executor.memory=3g,spark.executor.memoryOverhead=768m,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/livejournal-kryo-mem3g
  ```

# 6) 5g / 1024m, application_1757862796140_0003
gcloud dataproc jobs submit spark --cluster=baseline-cluster --region=europe-west3 \
  --class=CCJob --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.executor.memory=5g,spark.executor.memoryOverhead=1024m,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/livejournal-kryo-mem5g

# 7) 7g / 1536m, application_1757862796140_0004
gcloud dataproc jobs submit spark --cluster=baseline-cluster --region=europe-west3 \
  --class=CCJob --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.serializer=org.apache.spark.serializer.KryoSerializer,spark.executor.memory=7g,spark.executor.memoryOverhead=1536m,spark.eventLog.enabled=true,spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history,spark.default.parallelism=32,spark.sql.shuffle.partitions=32 \
  -- gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt gs://spark-memory-opt-bucket/out/cc/livejournal-kryo-mem7g
