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