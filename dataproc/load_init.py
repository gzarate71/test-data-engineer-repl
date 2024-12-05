from pyspark.sql import SparkSession
# create a spark session with mssql
spark = SparkSession.builder \
    .appName("sql-server-cdc-with-pyspark") \
    .config("spark.jars.packages", "com.microsoft.sqlserver:mssql-jdbc:9.4.1.jre8") \
    .getOrCreate()
# secrets included for readability; normally they would be in KeyVault, etc.
SRC_USER = "XXXXXX"
SRC_PWD  = "XXXXXX"
SRC_HOST = "XXXXXX"
SRC_DB   = "XXXXXX"
SRC_PORT   = "XXXXXX"

# TODO Change the table name and table primary key so that they point to the data to be replicated
src_table     = "your_table"
src_table_key = "your_table_pk"

# get the data and schema of the src table from sql server
df = spark.read \
        .format("jdbc") \
        .option("url", f"jdbc:sqlserver://{SRC_HOST}:{SRC_PORT}; database={SRC_DB}; fetchsize=20000") \
        .option("dbtable", f"dbo.{src_table}") \
        .option("user", SRC_USER) \
        .option("password", SRC_PWD) \
        .option("encrypt", "true") \
        .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
        .option("hostNameInCertificate", "*.database.windows.net") \
        .load()

sparkbq = SparkSession \
  .builder \
  .appName('spark-bigquery-demo') \
  .getOrCreate()

# Use the Cloud Storage bucket for temporary BigQuery export data used
# by the connector.
# TODO Change the bucket name to your bucket name
bucket = "YOUR_BUCKET"
sparkbq.conf.set('temporaryGcsBucket', bucket)

# Saving the data to BigQuery
df.write.format('bigquery') \
  .option('table', 'wordcount_dataset.wordcount_output') \
  .save()
