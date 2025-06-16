# SCD Type 2 Implementation for Large Delta Tables in Microsoft Fabric
# This notebook implements SCD Type 2 with upsert operations for tables with 130+ columns
# Utilizing Microsoft Fabric autotune optimization and best practices

# %%
# Cell 1: Import Required Libraries and Configure Spark Session
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import DeltaTable
import datetime
from pyspark.sql.window import Window

# Configure Spark session with autotune enabled
spark = SparkSession.builder \
    .appName("SCD_Type2_Large_Table") \
    .config("spark.databricks.optimizer.autotune.enabled", "true") \
    .config("spark.sql.parquet.vorder.enabled", "false") \
    .config("spark.databricks.delta.optimize.write.enabled", "true") \
    .config("spark.databricks.delta.optimizeWrite.binSize", "512") \
    .config("spark.sql.shuffle.partitions", "auto") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

print("Spark session configured with autotune and optimization settings")

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
    Generate surrogate keys for new records
    """
    # Get max surrogate key from target table
    try:
        max_key = spark.read.format("delta").load(target_table_path) \
            .selectExpr("max(surrogate_key) as max_key") \
            .collect()[0]["max_key"] or 0
    except:
        max_key = 0
    
    # Add row numbers and create surrogate keys
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
    
    # Cache if data size is manageable
    if source_df.count() < 10000000:  # Adjust threshold based on cluster size
        source_df.cache()
    
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
    Execute SCD Type 2 merge with optimizations for large tables
    """
    # Get DeltaTable reference
    target_table = DeltaTable.forPath(spark, target_table_path)
    
    # Identify changes
    new_records, changed_records, deleted_records = identify_changes(source_df, target_table_path)
    
    # Union new and changed records
    records_to_insert = new_records.unionByName(changed_records, allowMissingColumns=True)
    
    if records_to_insert.count() > 0:
        # Add SCD2 columns
        records_to_insert = add_scd2_columns(records_to_insert)
        records_to_insert = generate_surrogate_key(records_to_insert, target_table_path)
        
        # Create join condition for merge
        merge_condition = " AND ".join([f"source.{key} = target.{key}" for key in NATURAL_KEY_COLUMNS])
        merge_condition += " AND target.is_current = true"
        
        # Perform merge operation
        merge_builder = target_table.alias("target").merge(
            records_to_insert.alias("source"),
            merge_condition
        )
        
        # Update existing records - set end date and is_current flag
        merge_builder = merge_builder.whenMatchedUpdate(
            set={
                "to_date": current_timestamp(),
                "is_current": lit(False)
            }
        )
        
        # Insert new versions
        merge_builder = merge_builder.whenNotMatchedInsertAll()
        
        # Execute merge
        merge_builder.execute()
        
        print(f"Merged {records_to_insert.count()} records")
    
    # Handle deleted records
    if deleted_records.count() > 0:
        # Create condition for deleted records
        delete_conditions = []
        for _, row in deleted_records.toPandas().iterrows():
            cond = " AND ".join([f"{key} = '{row[key]}'" for key in NATURAL_KEY_COLUMNS])
            delete_conditions.append(f"({cond})")
        
        delete_condition = " OR ".join(delete_conditions) + " AND is_current = true"
        
        # Update deleted records
        target_table.update(
            condition=delete_condition,
            set={
                "to_date": current_timestamp(),
                "is_current": lit(False)
            }
        )
        
        print(f"Marked {deleted_records.count()} records as deleted")

# %%
# Cell 8: Optimize Delta Table Performance
def optimize_delta_table(table_path):
    """
    Apply optimization techniques for large delta tables
    """
    print(f"Starting optimization for {TARGET_TABLE_NAME}")
    
    # Run OPTIMIZE command with bin-packing
    spark.sql(f"""
        OPTIMIZE delta.`{table_path}`
        WHERE to_date >= current_date() - INTERVAL 7 DAYS
    """)
    
    # Apply Z-ORDER on frequently queried columns
    if NATURAL_KEY_COLUMNS:
        zorder_cols = ", ".join(NATURAL_KEY_COLUMNS[:2])  # Z-order on first 2 keys
        spark.sql(f"""
            OPTIMIZE delta.`{table_path}`
            ZORDER BY ({zorder_cols})
        """)
    
    # Run VACUUM to remove old files (keeping 7 days for time travel)
    spark.sql(f"""
        VACUUM delta.`{table_path}` RETAIN 168 HOURS
    """)
    
    # Compute statistics for better query performance
    spark.sql(f"""
        ANALYZE TABLE delta.`{table_path}` 
        COMPUTE STATISTICS
    """)
    
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
        
        # Load source data
        print("Loading source data...")
        source_df = load_source_data()
        print(f"Source records count: {source_df.count()}")
        
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
