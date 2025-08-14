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

## Create a job with baseline config
```bash
gcloud dataproc clusters create baseline-cluster \
  --region=europe-west3 \
  --zone=europe-west3-a \
  --master-machine-type=n2-standard-4 \
  --master-boot-disk-size=100GB \
  --num-workers=3 \
  --worker-machine-type=n2-standard-4 \
  --worker-boot-disk-size=100GB \
  --image-version=2.2-debian12 \
  --optional-components=JUPYTER \
  --enable-component-gateway \
  --properties spark:spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history


```

## Create a cluster for history server
```bash
gcloud dataproc clusters create history-server \
  --region=europe-west3 \
  --zone=europe-west3-a \
  --single-node \
  --master-machine-type=n2-standard-2 \
  --master-boot-disk-size=50GB \
  --image-version=2.2-debian12 \
  --optional-components=JUPYTER \
  --enable-component-gateway \
  --properties spark:spark.history.fs.logDirectory=gs://spark-memory-opt-bucket/spark-history
```