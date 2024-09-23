import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, from_unixtime, to_timestamp
from pyspark.sql.types import StructType, StructField, FloatType, DoubleType,IntegerType

# Read Kafka and TimescaleDB configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "")
DB_URL = os.getenv("DB_URL", "")
DB_TABLE = os.getenv("DB_TABLE", "sensor_data")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("IoTSensorDataKafkaToTimesScaleDB") \
    .getOrCreate()

# Define the schema for the sensor data
schema = StructType([
    StructField("sensor_id", IntegerType(), True),
    StructField("temperature", FloatType(), True),
    StructField("humidity", FloatType(), True),
    StructField("timestamp", DoubleType(), True)
])

# Read from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON data and convert Unix timestamp to SQL TIMESTAMP WITH TIME ZONE (TIMESTAMPTZ)
sensor_df = kafka_df.selectExpr("CAST(value AS STRING) as jsonString") \
    .withColumn("jsonData", from_json(col("jsonString"), schema)) \
    .select(
        col("jsonData.sensor_id"),
        col("jsonData.temperature"),
        col("jsonData.humidity"),
        to_timestamp(from_unixtime(col("jsonData.timestamp"))).alias("timestamp")  # Convert Unix timestamp to TIMESTAMP
    )

# Write to TimescaleDB
def write_to_db(batch_df, batch_id):
    if not batch_df.isEmpty():
        batch_df.write \
            .format("jdbc") \
            .option("url", DB_URL) \
            .option("dbtable", DB_TABLE) \
            .option("user", DB_USER) \
            .option("password", DB_PASSWORD) \
            .mode("append") \
            .save()

query = sensor_df.writeStream \
    .foreachBatch(write_to_db) \
    .outputMode("append") \
    .start()

# Wait for the query to finish
query.awaitTermination()

# Stop the Spark session
spark.stop()
