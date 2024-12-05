from pyspark.sql import SparkSession

# create a spark session with mssql and bigquery
spark = SparkSession.builder \
    .appName("sql-server-cdc-with-pyspark") \
    .config("spark.jars.packages", "com.microsoft.sqlserver:mssql-jdbc:9.4.1.jre8") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.21.1") \
    .config("spark.sql.repl.eagerEval.enabled", True) \
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

# get a list of fields from the existing object that we are interested in updating
cdc_fields = [x.name for x in spark.sql(f"select * from {src_table}").schema.fields]

spark.read \
        .format("jdbc") \
        .option("url", f"jdbc:sqlserver://{SRC_HOST}:{SRC_PORT}; database={SRC_DB}; fetchsize=20000") \
        .option("dbtable", f"cdc.dbo_{src_table}_CT") \
        .option("user", SRC_USER) \
        .option("password", SRC_PWD) \
        .option("encrypt", "true") \
        .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
        .option("hostNameInCertificate", "*.database.windows.net") \
        .load().createOrReplaceTempView(f"cdc_{src_table}")

# adjust the CDC data for the latest changes
df = spark.sql(f"""
WITH ranked_cdc_data AS (
  SELECT 
    *
--  ,CAST(CASE WHEN `__$operation` = 1 THEN 1 ELSE 0 END AS BOOLEAN) as deleted 
    ,CAST(CASE WHEN `__$operation` = 2 THEN 1 ELSE 0 END AS BOOLEAN) as inserted
--  ,CAST(CASE WHEN `__$operation` = 4 THEN 1 ELSE 0 END AS BOOLEAN) as updated
    ,ROW_NUMBER() OVER (PARTITION BY {src_table_key} ORDER BY `__$start_lsn` DESC, `__$operation` DESC) rank
  FROM 
    cdc_{src_table}
  WHERE `__$operation` != 3
),
latest_cdc_data AS (
  SELECT
    *
  FROM
    ranked_cdc_data
  WHERE rank = 1
  )
select * from latest_cdc_data
""").select(cdc_fields + ["inserted"])

# Use the Cloud Storage bucket for temporary BigQuery export data used
# by the connector.
# TODO Change the bucket name to your bucket name
bucket = "YOUR_BUCKET"
sparkbq.conf.set('temporaryGcsBucket', bucket)

# Update to your BigQuery dataset name you created
bq_dataset = 'your_dataset_name'

# Enter BigQuery table name you want to append. 
bq_table = 'your_table_name'

df.write \
  .format("bigquery") \
  .option("table","{}.{}".format(bq_dataset, bq_table)) \
  .option("temporaryGcsBucket", bucket) \
  .mode('append') \
  .save()
