# Microsoft Fabric PySpark Cheatsheet
*Based on verified Microsoft Fabric documentation and code examples*

## Essential Imports
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, current_timestamp, year, month
from pyspark.sql.types import *
from notebookutils import mssparkutils  # Updated namespace
```

## Microsoft Spark Utilities (MSSparkUtils)

### File System Operations
```python
# Import utilities
from notebookutils import mssparkutils

# List directory contents
mssparkutils.fs.ls("Files/tmp")  # Default lakehouse
mssparkutils.fs.ls("abfss://<container>@<account>.dfs.core.windows.net/<path>")

# View file properties
files = mssparkutils.fs.ls('directory_path')
for file in files:
    print(file.name, file.isDir, file.isFile, file.path, file.size)

# Create directories
mssparkutils.fs.mkdirs('new_directory_name')
mssparkutils.fs.mkdirs("Files/<new_dir>")  # Default lakehouse

# Copy files/directories
mssparkutils.fs.cp('source', 'destination', True)  # True for recursive

# Fast copy for large volumes
mssparkutils.fs.fastcp('source', 'destination', True)

# Move files/directories
mssparkutils.fs.mv('source', 'destination', True)  # True to create parent dirs

# Preview file content
mssparkutils.fs.head('file_path', 1024)  # maxBytes parameter

# Write to file
mssparkutils.fs.put("file_path", "content", True)  # True to overwrite

# Append to file
mssparkutils.fs.append("file_path", "content", True)  # True to create if not exists

# Delete files/directories
mssparkutils.fs.rm('file_path', True)  # True for recursive
```

### Mount Operations
```python
# Mount ADLS Gen2 with account key
accountKey = mssparkutils.credentials.getSecret("<vaultURI>", "<secretName>")
mssparkutils.fs.mount(
    "abfss://mycontainer@<accountname>.dfs.core.windows.net",
    "/test",
    {"accountKey": accountKey}
)

# Mount with SAS token
sasToken = mssparkutils.credentials.getSecret("<vaultURI>", "<secretName>")
mssparkutils.fs.mount(
    "abfss://mycontainer@<accountname>.dfs.core.windows.net",
    "/test",
    {"sasToken": sasToken}
)

# Mount a lakehouse
mssparkutils.fs.mount(
    "abfss://<workspace_id>@onelake.dfs.fabric.microsoft.com/<lakehouse_id>",
    "/test"
)

# Access mounted files
path = mssparkutils.fs.getMountPath("/test")
mssparkutils.fs.ls(f"file://{path}")

# Check existing mount points
mssparkutils.fs.mounts()

# Unmount
mssparkutils.fs.unmount("/test")
```

### Notebook Operations
```python
# Run another notebook
exitVal = mssparkutils.notebook.run("NotebookName", 90, {"param": "value"})

# Run notebook in different workspace
exitVal = mssparkutils.notebook.run("NotebookName", 90, {"param": "value"}, "workspace_id")

# Run multiple notebooks in parallel
mssparkutils.notebook.runMultiple(["Notebook1", "Notebook2"])

# Run with dependencies (DAG structure)
DAG = {
    "activities": [
        {
            "name": "NotebookSimple",
            "path": "NotebookSimple",
            "timeoutPerCellInSeconds": 90,
            "args": {"p1": "value", "p2": 100}
        },
        {
            "name": "NotebookSimple2",
            "path": "NotebookSimple2",
            "timeoutPerCellInSeconds": 120,
            "args": {"p1": "value2", "p2": 200},
            "dependencies": ["NotebookSimple"]
        }
    ],
    "timeoutInSeconds": 43200,
    "concurrency": 50
}
mssparkutils.notebook.runMultiple(DAG)

# Exit notebook with value
mssparkutils.notebook.exit("exit_value")
```

### Credentials & Security
```python
# Get access tokens
token = mssparkutils.credentials.getToken('storage')  # Storage audience
token = mssparkutils.credentials.getToken('pbi')      # Power BI
token = mssparkutils.credentials.getToken('keyvault') # Key Vault
token = mssparkutils.credentials.getToken('kusto')    # Synapse RTA KQL DB

# Get secrets from Key Vault
secret = mssparkutils.credentials.getSecret('https://<keyvault>.vault.azure.net/', 'secret_name')
```

### Lakehouse Management
```python
# Create lakehouse artifact
artifact = mssparkutils.lakehouse.create("artifact_name", "Description", "workspace_id")

# Get lakehouse artifact
artifact = mssparkutils.lakehouse.get("artifact_name", "workspace_id")

# Update lakehouse artifact
updated_artifact = mssparkutils.lakehouse.update("old_name", "new_name", "Updated description", "workspace_id")

# Delete lakehouse artifact
is_deleted = mssparkutils.lakehouse.delete("artifact_name", "workspace_id")

# List all lakehouse artifacts
artifacts_list = mssparkutils.lakehouse.list("workspace_id")
```

### Runtime Context
```python
# Get session context information
context = mssparkutils.runtime.context
print(context)  # Shows notebook name, default lakehouse, workspace info, etc.
```

## DataFrame Operations

### Reading Data
```python
# Read from Parquet
df = spark.read.parquet("Files/data/orders.parquet")

# Read from CSV
df = spark.read.option("header", "true").csv("Files/data/orders.csv")

# Read from Delta table
df = spark.read.format("delta").load("Tables/orders")

# Read with schema
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True)
])
df = spark.read.schema(schema).csv("Files/data/orders.csv", header=True)
```

### Data Transformations
```python
# Add columns with current timestamp
from pyspark.sql.functions import col, to_timestamp, current_timestamp, year, month

df_with_timestamp = df.withColumn("dataload_datetime", current_timestamp())

# Add year and month columns
df_with_date_parts = df_with_timestamp \
    .withColumn("year", year(col("date_column"))) \
    .withColumn("month", month(col("date_column")))

# Select specific columns
df_selected = df.select("col1", "col2", col("col3").alias("new_name"))

# Filter data
df_filtered = df.filter(col("amount") > 100)

# Group by and aggregate
df_grouped = df.groupBy("category").agg(
    {"amount": "sum", "quantity": "avg"}
)
```

### Writing Data
```python
# Write to Parquet
df.write.mode("overwrite").parquet("Files/output/data.parquet")

# Write to Delta table
df.write.format("delta").mode("overwrite").saveAsTable("orders_processed")

# Write to Fabric Data Warehouse
df.write.synapsesql("<warehouse_name>.<schema_name>.<table_name>")

# Write with specific mode
df.write.mode("errorifexists").synapsesql("<warehouse_name>.<schema_name>.<table_name>")
df.write.mode("append").synapsesql("<warehouse_name>.<schema_name>.<table_name>")
df.write.mode("overwrite").synapsesql("<warehouse_name>.<schema_name>.<table_name>")
```

## Spark SQL Integration

### Using SQL Magic
```python
# In notebook cell, use %%sql magic
%%sql
SELECT * FROM salesorders LIMIT 1000
```

### Embedding SQL in PySpark
```python
# Create temporary view
df.createOrReplaceTempView("temp_orders")

# Execute SQL query
result_df = spark.sql("SELECT * FROM temp_orders WHERE amount > 100")

# Query lakehouse tables directly
df = spark.sql("SELECT * FROM [lakehouse_name].table_name LIMIT 1000")
```

## Display and Visualization
```python
# Display DataFrame
display(df)

# Show DataFrame (basic)
df.show()

# Show with specific number of rows
df.show(20)

# Collect data to driver (use with caution)
data = df.collect()

# Get schema information
df.printSchema()

# Get basic statistics
df.describe().show()
```

## Common Data Processing Patterns
```python
# Load, transform, and save pattern
raw_df = spark.read.parquet("Files/raw/data.parquet")

processed_df = raw_df \
    .withColumn("dataload_datetime", current_timestamp()) \
    .withColumn("year", year(col("date_column"))) \
    .withColumn("month", month(col("date_column"))) \
    .filter(col("status") == "active")

processed_df.write.format("delta").mode("overwrite").saveAsTable("processed_data")

# Create relational view and query
processed_df.createOrReplaceTempView("processed_view")
result = spark.sql("""
    SELECT year, month, COUNT(*) as record_count
    FROM processed_view
    GROUP BY year, month
    ORDER BY year, month
""")
display(result)
```

## Best Practices

### Performance Optimization
```python
# Cache frequently used DataFrames
df.cache()

# Persist with specific storage level
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)

# Unpersist when done
df.unpersist()

# Repartition for better parallelism
df_repartitioned = df.repartition(10)

# Coalesce to reduce partitions
df_coalesced = df.coalesce(5)
```

### Error Handling
```python
try:
    df = spark.read.parquet("Files/data/orders.parquet")
    result = df.count()
    print(f"Successfully read {result} records")
except Exception as e:
    print(f"Error reading data: {str(e)}")
```

### Memory Management
```python
# Clear cache
spark.catalog.clearCache()

# Check active streams
spark.streams.active

# Stop all streaming queries
for stream in spark.streams.active:
    stream.stop()
```

## Fabric-Specific Features

### Lakehouse Integration
```python
# Access default lakehouse files
files = mssparkutils.fs.ls("Files/")

# Access lakehouse tables
tables = mssparkutils.fs.ls("Tables/")

# Read from lakehouse table
df = spark.read.format("delta").load("Tables/table_name")
```

### OneLake Integration
```python
# Access OneLake paths
onelake_path = "abfss://workspace_id@onelake.dfs.fabric.microsoft.com/lakehouse_id/Files/"
df = spark.read.parquet(onelake_path + "data.parquet")
```

### Notebook Resources
```python
# Use notebook resources path
resource_path = mssparkutils.nbResPath
config_df = spark.read.json(f"{resource_path}/config.json")
```

This cheatsheet covers the most commonly used PySpark operations in Microsoft Fabric, based on verified code examples from Microsoft's official documentation.
