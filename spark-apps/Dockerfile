# Use the official Spark image as the base image
FROM apache/spark:3.4.3

# Create directories to hold your application code and jars
RUN mkdir -p /tmp/spark-apps

# Copy the Python ETL script to the /tmp/spark-apps directory
COPY ./kafka-to-timescaledb/spark-kafka-to-timescaledb-app.py /tmp/spark-apps/

# Download and place JARs into Spark's JARs directory
RUN wget https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar -P $SPARK_HOME/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar -P $SPARK_HOME/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.4.3/spark-sql-kafka-0-10_2.12-3.4.3.jar -P $SPARK_HOME/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.4.3/spark-token-provider-kafka-0-10_2.12-3.4.3.jar -P $SPARK_HOME/jars/
RUN wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.4/postgresql-42.7.4.jar -P $SPARK_HOME/jars/