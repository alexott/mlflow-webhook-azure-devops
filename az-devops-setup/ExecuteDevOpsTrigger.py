# Databricks notebook source
dbutils.widgets.text(name = "model_name", defaultValue = "unknown model", label = "Model Name")
dbutils.widgets.text(name = "version", defaultValue="-1",label = "Version")
dbutils.widgets.text(name = "stage", defaultValue="Unknown",label = "To Stage")
dbutils.widgets.text(name = "timestamp", defaultValue="0",label = "Version")
dbutils.widgets.text(name = "text", defaultValue="",label = "Version")
dbutils.widgets.text(name = "webhook_id", defaultValue="",label = "Version")

# COMMAND ----------

dict = { 
  'model_name': dbutils.widgets.get("model_name"),
  'version': dbutils.widgets.get("version"),
  'stage': dbutils.widgets.get("stage"),
  'timestamp': dbutils.widgets.get("timestamp"),
  'text': dbutils.widgets.get("text"),
  'webhook_id': dbutils.widgets.get("webhook_id")
}

# COMMAND ----------

from pyspark.sql import Row
import pyspark.sql.functions as F
df = spark.createDataFrame(Row(dict)).withColumn("run_ts", F.current_timestamp())

# COMMAND ----------

df.write.format("delta").mode("append").option("mergeSchema", "true").save("/tmp/alexey.ott/mlflow-runs/")

# COMMAND ----------

#display(spark.read.format("delta").load("/tmp/alexey.ott/mlflow-runs/"))

# COMMAND ----------


