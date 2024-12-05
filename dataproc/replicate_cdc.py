from pyspark.sql import SparkSession

# create a spark session with mssql, delta, and hive support enabled
spark = SparkSession.builder \
    .appName("sql-server-cdc-with-pyspark") \
    .config("spark.jars.packages", "com.microsoft.sqlserver:mssql-jdbc:9.4.1.jre8") \
    .getOrCreate()
# secrets included for readability; normally they would be in KeyVault, etc.
SRC_USER = "XXXXXX"
SRC_PWD  = "XXXXXX"
SRC_HOST = "XXXXXX"
SRC_DB   = "XXXXXX"

src_table     = "customers"
src_table_key = "customer_id"

# get a list of fields from the existing object that we are interested in updating
cdc_fields = [x.name for x in spark.sql(f"select * from {src_table}").schema.fields]

spark.read \
        .format("jdbc") \
        .option("url", f"jdbc:sqlserver://{SRC_HOST}:{SRC_PORT}; database={SRC_DB}; fetchsize=20000") \
        .option("dbtable", f"cdc.dbo_{src_table}_CT") \
        .option("user", SRC_USER) \
