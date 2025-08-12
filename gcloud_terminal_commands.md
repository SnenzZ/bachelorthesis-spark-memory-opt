## So erstellt man einen Single Node Cluster

```bash
gcloud dataproc clusters create graphx-cluster \
  --region=europe-west3 \
  --single-node \
  --image-version=2.2-debian12 \
  --enable-component-gateway \
  --properties="spark:spark.eventLog.enabled=true,\
spark:spark.eventLog.dir=gs://spark-memory-opt-bucket/spark-history,\
spark:spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history"
```


## Upload file to a bucket in gcp
```bash
gsutil cp target/scala-2.12/spark-memory-opt-assembly-0.1.jar gs://spark-memory-opt-bucket/jars/
```

## Create a job
```bash
gcloud dataproc jobs submit spark \
  --region=europe-west3 \
  --cluster=cc-single \
  --class=CCJob \
  --jars=gs://spark-memory-opt-bucket/jars/spark-memory-opt-assembly-0.1.jar \
  --properties=spark.executor.instances=1,spark.executor.cores=2,spark.executor.memory=4g,spark.driver.memory=4g \
  -- gs://spark-memory-opt-bucket/data/web-Google.txt gs://spark-memory-opt-bucket/out/cc-webgoogle

```