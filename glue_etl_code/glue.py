from datetime import datetime
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import current_timestamp, col, sha2, concat_ws

# --------------------------------------------------
# Glue Context
# --------------------------------------------------
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# --------------------------------------------------
# S3 paths (CHANGE BUCKET NAME)
# --------------------------------------------------
source_path = "s3://testing-incremental-job/raw_data/"
raw_path    = "s3://testing-incremental-job/daily_incr_data/"

load_dttm = datetime.now().strftime("%Y%m%d_%H%M%S")
load_path = f"{raw_path}{load_dttm}/"

primary_key = "order_id"

print("Load path:", load_path)

# --------------------------------------------------
# 1️⃣ CREATE SAMPLE DATA (YOUR DATA)
# --------------------------------------------------
data = [
    ("101","C001",250,"DELIVERED","2024-12-01 09:35:21"),
    ("102","C002",0,"CANCELLED","2024-12-01 09:36:10"),
    ("103","C001",400,"DELIVERED","2024/12/01 10:01:45"),
    ("104","C003",150,"DELIVERED","2024-12-01T10:30:10Z"),
    ("105","C004",50,"DELIVERED","2024-12-01 11:00:00"),
    ("106","C002",400,"DELIVERED","12-01-2024 11:05:50"),
    ("107","C003",700,"DELIVERED","2024-12-01 12:10:20"),
    ("108","C001",250,"DELIVERED","2024-12-01 13:25:40"),
    ("109","C002",11000,"DELIVERED","12-01-2024 11:05:50"),
    ("110","C003",11700,"DELIVERED","2024-12-01 12:10:20"),
    ("111","C003",11700,"DELIVERED","2024-12-01 12:10:20"),
    ("112","C003",1700,"DELIVERED","2024-12-01 12:10:20"),
    ("113","C003",1700,"DELIVERED","2024-12-01 12:10:20")
]

columns = ["order_id","customer_id","amount","status","order_timestamp"]

df_seed = spark.createDataFrame(data, columns)

# --------------------------------------------------
# 2️⃣ WRITE SOURCE CSV (LANDING ZONE)
# --------------------------------------------------
df_seed.coalesce(1) \
    .write.mode("overwrite") \
    .option("header", True) \
    .csv(source_path)

print("Source data written")
print("source data is not written to s3")

# --------------------------------------------------
# 3️⃣ READ SOURCE CSV
# --------------------------------------------------
source_df = (
    spark.read
        .option("header", True)
        .csv(source_path)
        .withColumn("ingestion_date", current_timestamp())
)

# --------------------------------------------------
# 4️⃣ CREATE ROW HASH
# --------------------------------------------------
cols_for_hash = [c for c in source_df.columns if c not in ["ingestion_date", "row_hash"]]

source_df = source_df.withColumn(
    "row_hash",
    sha2(concat_ws("||", *[col(c) for c in cols_for_hash]), 256)
)

# --------------------------------------------------
# 5️⃣ CHECK FOR PREVIOUS DATA
# --------------------------------------------------
try:
    prev_df = spark.read.json(f"{raw_path}*")  # <-- include all folders
    prev_count = prev_df.count()
    
    if prev_count == 0:
        raise Exception("Previous data empty")
    
    first_load = False
    print(f"Previous data found ({prev_count} rows) → INCREMENTAL LOAD")

except Exception as e:
    print("TRY BLOCK ERROR:", e)
    prev_df = None
    first_load = True
    print("No previous data → FULL LOAD")

# --------------------------------------------------
# 6️⃣ FULL LOAD
# -------------------------------
if first_load:
    source_df.write.mode("overwrite").json(load_path)
    print(f"FULL LOAD completed → {load_path}")
else:
    incre_load=source_df.alias("src").join(prev_df.alias("prev"),"order_id","left")\
                                    .filter("prev.row_hash is null or src.row_hash!=prev.row_hash")\
                                    .select("src.*") 
   
    incr_count=incre_load.count()
    print(f"Incremental rows detected → {incr_count}")
    if incr_count > 0:
        incre_load.write.mode("overwrite").json(load_path)
        print(f"INCREMENTAL LOAD completed → {load_path}")
    else:
        print("No new or changed rows.")