# SCD Type 2 Implementation for Large Delta Tables in Microsoft Fabric
# This notebook implements SCD Type 2 with upsert operations for tables with 130+ columns
# Utilizing Microsoft Fabric autotune optimization and best practices

# %%
# Cell 1: Import Required Libraries and Configure the Spark Session
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import DeltaTable
import datetime
from pyspark.sql.window import Window

# NOTE (Fabric): a notebook already has a ready-to-use `spark` session backed by
# the workspace's Live Pool. Do NOT build your own SparkSession with
# SparkSession.builder / getOrCreate() -- just use the provided `spark` object and
# tune it at runtime with spark.conf.set(...). (The former builder here also used
# Databricks-only config keys that are silently ignored on Fabric.)

# --- Fabric autotune (verified key) ---
# Correct key is spark.ms.autotune.enabled (the old spark.databricks.optimizer.*
# key does nothing on Fabric). Autotune is a preview feature, OFF by default, and
# is only honored on Runtime 1.2; on newer runtimes this config is simply ignored,
# so it is safe to set. It auto-tunes shuffle partitions, broadcast-join threshold
# and max partition bytes per query -- which is why we no longer hard-code them.
spark.conf.set("spark.ms.autotune.enabled", "true")

# --- Optimized Write (verified Fabric keys) ---
# Fabric's Delta writer uses the spark.microsoft.delta.* namespace. Optimized write
# does pre-write bin-packing so MERGE/UPDATE/DELETE produce fewer, larger files.
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
# Target bin size in BYTES (1 GiB), matching the official Fabric lakehouse tutorial.
spark.conf.set("spark.microsoft.delta.optimizeWrite.binSize", "1073741824")

# --- V-Order ---
# Left OFF here because this is a write-heavy MERGE workload (V-Order adds write
# overhead). If this dimension is primarily read by Power BI / Direct Lake, set
# this to "true" (or run OPTIMIZE ... VORDER) for better read performance.
spark.conf.set("spark.sql.parquet.vorder.enabled", "false")

# --- Adaptive Query Execution ---
# AQE is enabled by default on Fabric and adapts shuffle partition counts at
# runtime, so we intentionally do NOT set spark.sql.shuffle.partitions
# (the old value "auto" is invalid -- that setting expects an integer).
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

print("Spark session configured with Fabric autotune and optimized-write settings")

# %%
# Cell 2: Define Configuration Parameters
# Update these parameters based on your environment
WORKSPACE_NAME = "your_workspace_name"
LAKEHOUSE_NAME = "your_lakehouse_name"
SOURCE_TABLE_NAME = "source_table"
TARGET_TABLE_NAME = "target_dimension_table"
LAKEHOUSE_PATH = f"abfss://workspace@onelake.dfs.fabric.microsoft.com/{WORKSPACE_NAME}/{LAKEHOUSE_NAME}"

# SCD Type 2 configuration
NATURAL_KEY_COLUMNS = ["customer_id", "product_id"]  # Add your natural key columns
HASH_COLUMNS = []  # Columns to track for changes (leave empty to track all non-key columns)
EXCLUDED_COLUMNS = ["etl_timestamp", "source_system"]  # Columns to exclude from change detection

# Performance tuning for large column count
BATCH_SIZE = 100000  # Process data in batches for better memory management
PARTITION_COLUMNS = ["year", "month"]  # Add partition columns if applicable

# %%
# Cell 3: Utility Functions for SCD Type 2
def generate_hash_key(df, columns_to_hash):
    """
    Generate a hash key for change detection across multiple columns
    """
    if not columns_to_hash:
        # If no specific columns specified, use all columns except keys and metadata
        columns_to_hash = [col for col in df.columns 
                          if col not in NATURAL_KEY_COLUMNS + EXCLUDED_COLUMNS + 
                          ["surrogate_key", "from_date", "to_date", "is_current", "hash_key"]]
    
    # Create hash expression for all columns
    hash_expr = concat_ws("||", *[coalesce(col(c).cast("string"), lit("")) for c in columns_to_hash])
    
    return df.withColumn("hash_key", sha2(hash_expr, 256))

def add_scd2_columns(df):
    """
    Add SCD Type 2 tracking columns to dataframe
    """
    return df \
        .withColumn("from_date", current_timestamp()) \
        .withColumn("to_date", lit("9999-12-31 23:59:59").cast("timestamp")) \
        .withColumn("is_current", lit(True))

def generate_surrogate_key(df, target_table_path):
    """
    Generate surrogate keys for new records.

    LIMITATION: row_number() over Window.orderBy(lit(1)) forces every row into a
    single partition to compute a global sequence, which does not scale and is NOT
    safe under concurrent writers (two jobs can read the same max and collide).
    It is kept here because it is simple and adequate for a single-writer batch
    demo. For production consider one of:
      * a Delta IDENTITY column on surrogate_key (GENERATED ALWAYS AS IDENTITY),
      * monotonically_increasing_id() + max_key (non-contiguous but cheap), or
      * an external sequence generated once per pipeline run.
    """
    # Get max surrogate key from target table
    try:
        max_key = spark.read.format("delta").load(target_table_path) \
            .selectExpr("max(surrogate_key) as max_key") \
            .collect()[0]["max_key"] or 0
    except Exception:
        max_key = 0

    # Add row numbers and create surrogate keys (see LIMITATION above).
    window_spec = Window.orderBy(lit(1))
    return df.withColumn("surrogate_key", row_number().over(window_spec) + max_key)

# %%
# Cell 4: Load Source Data with Optimization for Large Column Count
def load_source_data():
    """
    Load source data with optimizations for tables with many columns
    """
    # Read source data
    source_df = spark.read \
        .format("delta") \
        .option("mergeSchema", "true") \
        .load(f"{LAKEHOUSE_PATH}/Tables/{SOURCE_TABLE_NAME}")
    
    # Add hash key for change detection
    source_df = generate_hash_key(source_df, HASH_COLUMNS)

    # Cache once: the source is scanned multiple times downstream (new/changed/
    # deleted detection, then again for the insert set), so materialize it now and
    # reuse a single row count instead of recomputing it in the caller.
    source_df.cache()
    source_count = source_df.count()  # single action; also warms the cache
    print(f"Source records count: {source_count:,}")

    return source_df

# %%
# Cell 5: Initialize Target Table if Not Exists
def initialize_target_table(source_df):
    """
    Create target table with SCD2 structure if it doesn't exist
    """
    target_path = f"{LAKEHOUSE_PATH}/Tables/{TARGET_TABLE_NAME}"
    
    if not DeltaTable.isDeltaTable(spark, target_path):
        print(f"Creating new target table: {TARGET_TABLE_NAME}")
        
        # Add SCD2 columns to source schema
        initial_df = source_df.limit(0)  # Get schema only
        initial_df = add_scd2_columns(initial_df)
        initial_df = initial_df.withColumn("surrogate_key", lit(0).cast("long"))
        
        # Write initial empty table
        initial_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(target_path)
        
        # Create table in metastore
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {TARGET_TABLE_NAME}
            USING DELTA
            LOCATION '{target_path}'
        """)
        
        print(f"Target table {TARGET_TABLE_NAME} created successfully")
    
    return target_path

# %%
# Cell 6: Identify Changes Using MERGE Strategy
def identify_changes(source_df, target_table_path):
    """
    Identify new and changed records for SCD Type 2
    """
    # Load current records from target
    target_df = spark.read.format("delta").load(target_table_path) \
        .filter(col("is_current") == True)
    
    # Create natural key expression for joining
    join_conditions = [source_df[key] == target_df[key] for key in NATURAL_KEY_COLUMNS]
    join_condition = join_conditions[0]
    for cond in join_conditions[1:]:
        join_condition = join_condition & cond
    
    # Find new records (not in target)
    new_records = source_df.join(
        target_df.select(*NATURAL_KEY_COLUMNS).distinct(),
        NATURAL_KEY_COLUMNS,
        "left_anti"
    )
    
    # Find changed records (hash key different)
    changed_records = source_df.alias("s").join(
        target_df.alias("t"),
        join_condition & (col("s.hash_key") != col("t.hash_key")),
        "inner"
    ).select("s.*")
    
    # Find deleted records (in target but not in source)
    deleted_records = target_df.join(
        source_df.select(*NATURAL_KEY_COLUMNS).distinct(),
        NATURAL_KEY_COLUMNS,
        "left_anti"
    ).select(*NATURAL_KEY_COLUMNS)
    
    return new_records, changed_records, deleted_records

# %%
# Cell 7: Perform SCD Type 2 MERGE Operation
def perform_scd2_merge(source_df, target_table_path):
    """
    Execute the SCD Type 2 upsert.

    This is split into three explicit, set-based steps because a single MERGE
    keyed on the natural key CANNOT do SCD2 correctly: for a *changed* record the
    natural key matches the current row, so whenMatchedUpdate expires it, but
    whenNotMatchedInsertAll never fires for that key -- the NEW version is lost.
    (That was the original data-loss bug.)

    Correct approach:
      Step 1 - EXPIRE the current row of every CHANGED natural key (MERGE ...
               whenMatchedUpdate). No inserts happen in this MERGE.
      Step 2 - INSERT the new current version for BOTH new keys and changed keys
               (append the fresh rows produced from the source).
      Step 3 - EXPIRE current rows whose natural key disappeared from the source
               (logical delete), using a set-based MERGE (no toPandas/driver
               collect, and it works for string keys).

    IMPORTANT: Step 3 assumes `source_df` is a FULL snapshot of the entity. If you
    feed incremental/delta batches, remove the delete handling or it will wrongly
    expire everything not present in the current batch.
    """
    # Get DeltaTable reference
    target_table = DeltaTable.forPath(spark, target_table_path)

    # Identify changes once and cache the reused sets.
    new_records, changed_records, deleted_records = identify_changes(source_df, target_table_path)
    new_records.cache()
    changed_records.cache()
    deleted_records.cache()

    # Natural-key join predicate used by every step (composite-key safe).
    key_match = " AND ".join([f"source.{key} = target.{key}" for key in NATURAL_KEY_COLUMNS])

    # --- Step 1: expire the current version of changed records ---
    changed_count = changed_records.count()
    if changed_count > 0:
        target_table.alias("target").merge(
            changed_records.alias("source"),
            f"{key_match} AND target.is_current = true"
        ).whenMatchedUpdate(
            set={
                "to_date": current_timestamp(),
                "is_current": lit(False)
            }
        ).execute()
        print(f"Expired {changed_count:,} changed record(s)")

    # --- Step 2: insert the new current version for new AND changed keys ---
    # New keys have no current row yet; changed keys had theirs expired in Step 1.
    # Both need a brand-new current row, so we append them (not MERGE) which avoids
    # the "new version never inserted" bug entirely.
    records_to_insert = new_records.unionByName(changed_records, allowMissingColumns=True)
    insert_count = records_to_insert.count()
    if insert_count > 0:
        records_to_insert = add_scd2_columns(records_to_insert)
        records_to_insert = generate_surrogate_key(records_to_insert, target_table_path)

        # Align to the target schema and append as new current rows.
        target_cols = spark.read.format("delta").load(target_table_path).columns
        records_to_insert = records_to_insert.select(
            [col(c) for c in target_cols if c in records_to_insert.columns]
        )
        records_to_insert.write.format("delta").mode("append").save(target_table_path)
        print(f"Inserted {insert_count:,} new current record(s) (new + changed versions)")

    # --- Step 3: logical delete of records that vanished from the source ---
    delete_count = deleted_records.count()
    if delete_count > 0:
        # Set-based MERGE: expire current target rows whose natural key is in the
        # deleted set. No driver-side collect, and correct for string keys.
        target_table.alias("target").merge(
            deleted_records.alias("source"),
            f"{key_match} AND target.is_current = true"
        ).whenMatchedUpdate(
            set={
                "to_date": current_timestamp(),
                "is_current": lit(False)
            }
        ).execute()
        print(f"Marked {delete_count:,} record(s) as deleted")

# %%
# Cell 8: Optimize Delta Table Performance
def optimize_delta_table(table_path):
    """
    Apply optimization techniques for large delta tables
    """
    print(f"Starting optimization for {TARGET_TABLE_NAME}")

    # Run OPTIMIZE with Z-ORDER in a SINGLE command.
    # Fixes:
    #  * The old code scoped OPTIMIZE with `WHERE to_date >= ...`. An OPTIMIZE
    #    WHERE predicate is evaluated against file-level statistics; scoping on a
    #    frequently-rewritten metadata column like to_date is unreliable and the
    #    original also ran OPTIMIZE twice (full table, then again for Z-ORDER).
    #    If you want incremental maintenance, scope the WHERE on a PARTITION
    #    column instead, e.g. `WHERE year = 2026 AND month = 7`.
    #  * Z-Order and compaction are combined so files are only rewritten once.
    if NATURAL_KEY_COLUMNS:
        zorder_cols = ", ".join(NATURAL_KEY_COLUMNS[:2])  # Z-order on first 2 keys
        spark.sql(f"""
            OPTIMIZE delta.`{table_path}`
            ZORDER BY ({zorder_cols})
        """)
    else:
        spark.sql(f"OPTIMIZE delta.`{table_path}`")

    # Run VACUUM to remove old files. 168 HOURS == 7 days, the Fabric default
    # retention floor; going lower breaks time travel and can hit concurrent
    # readers/writers (and triggers the retention-duration safety check).
    spark.sql(f"""
        VACUUM delta.`{table_path}` RETAIN 168 HOURS
    """)

    # NOTE: Delta on Fabric auto-collects column statistics on write (used for
    # data skipping), so an explicit ANALYZE TABLE ... COMPUTE STATISTICS is not
    # required for file skipping. It is left out here; if you want cost-based
    # optimizer stats, run it against the registered table name (ANALYZE against
    # a delta.`path` reference is not supported), e.g.:
    #   spark.sql(f"ANALYZE TABLE {TARGET_TABLE_NAME} COMPUTE STATISTICS")

    print("Optimization completed")

# %%
# Cell 9: Main Execution Function
def execute_scd2_pipeline():
    """
    Main execution function for SCD Type 2 pipeline
    """
    try:
        # Start timestamp
        start_time = datetime.datetime.now()
        print(f"Starting SCD Type 2 pipeline at {start_time}")
        
        # Load source data (load_source_data caches and prints the row count once)
        print("Loading source data...")
        source_df = load_source_data()

        # Initialize target table if needed
        target_path = initialize_target_table(source_df)
        
        # Perform SCD2 merge
        print("Performing SCD Type 2 merge...")
        perform_scd2_merge(source_df, target_path)
        
        # Optimize table
        print("Optimizing delta table...")
        optimize_delta_table(target_path)
        
        # Calculate execution time
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Pipeline completed successfully in {duration:.2f} seconds")
        
        # Display sample of current records
        print("\nSample of current records:")
        spark.sql(f"""
            SELECT * FROM {TARGET_TABLE_NAME} 
            WHERE is_current = true 
            LIMIT 10
        """).show(truncate=False)
        
    except Exception as e:
        print(f"Error in SCD2 pipeline: {str(e)}")
        raise

# %%
# Cell 10: Execute Pipeline
# Run the SCD Type 2 pipeline
execute_scd2_pipeline()

# %%
# Cell 11: Create Views for Easy Querying
# Create a view for current records only
spark.sql(f"""
    CREATE OR REPLACE VIEW {TARGET_TABLE_NAME}_current AS
    SELECT * FROM {TARGET_TABLE_NAME}
    WHERE is_current = true
""")

# Create a view for historical analysis
spark.sql(f"""
    CREATE OR REPLACE VIEW {TARGET_TABLE_NAME}_history AS
    SELECT 
        *,
        CASE 
            WHEN is_current THEN 'Active'
            WHEN to_date < current_timestamp() THEN 'Expired'
            ELSE 'Unknown'
        END as record_status
    FROM {TARGET_TABLE_NAME}
""")

print("Views created successfully")

# %%
# Cell 12: Performance Monitoring and Statistics
def display_table_statistics():
    """
    Display performance statistics and table health metrics
    """
    # Get table statistics
    stats = spark.sql(f"""
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN is_current THEN 1 ELSE 0 END) as current_records,
            SUM(CASE WHEN NOT is_current THEN 1 ELSE 0 END) as historical_records,
            COUNT(DISTINCT {', '.join(NATURAL_KEY_COLUMNS)}) as unique_entities,
            MIN(from_date) as earliest_record,
            MAX(from_date) as latest_record
        FROM {TARGET_TABLE_NAME}
    """).collect()[0]
    
    print("Table Statistics:")
    print(f"Total Records: {stats['total_records']:,}")
    print(f"Current Records: {stats['current_records']:,}")
    print(f"Historical Records: {stats['historical_records']:,}")
    print(f"Unique Entities: {stats['unique_entities']:,}")
    print(f"Date Range: {stats['earliest_record']} to {stats['latest_record']}")
    
    # Get file statistics
    file_stats = spark.sql(f"""
        DESCRIBE DETAIL delta.`{LAKEHOUSE_PATH}/Tables/{TARGET_TABLE_NAME}`
    """).select("numFiles", "sizeInBytes").collect()[0]
    
    print(f"\nFile Statistics:")
    print(f"Number of Files: {file_stats['numFiles']}")
    print(f"Total Size: {file_stats['sizeInBytes'] / (1024**3):.2f} GB")

# Display statistics
display_table_statistics()

# %%
# Cell 13: Schedule Optimization (for production use)
# This cell shows how to schedule regular maintenance
print("""
To schedule regular maintenance in production:

1. Create a Data Pipeline in Microsoft Fabric
2. Add a Notebook activity pointing to this notebook
3. Set schedule (recommended: daily for active tables)
4. Configure the following pipeline parameters:
   - source_table: {SOURCE_TABLE_NAME}
   - target_table: {TARGET_TABLE_NAME}
   - optimize_frequency: 'daily' or 'weekly'
   
5. Add error handling and notifications
""")

# %%
# Cell 14: Advanced Performance Tips for 130+ Column Tables
print("""
Performance Tips for Tables with 130+ Columns:

1. Column Pruning:
   - Only select required columns in queries
   - Use column statistics for query optimization

2. Partitioning Strategy:
   - Partition by date columns if applicable
   - Avoid over-partitioning (max 1000 partitions)

3. File Size Management:
   - Target file size: 256MB - 1GB
   - Use optimize write for automatic file sizing

4. Caching Strategy:
   - Cache frequently accessed dimension data
   - Use broadcast joins for small dimensions

5. Autotune Configuration:
   - Enable autotune for automatic optimization
   - Monitor query performance metrics

6. Change Detection:
   - Use hash-based change detection for efficiency
   - Consider column groups for partial updates
""")
