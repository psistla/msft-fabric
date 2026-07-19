# Microsoft Fabric PySpark Cheatsheet
*Based on verified Microsoft Fabric documentation and code examples*

> **Namespace note:** MSSparkUtils was officially renamed to **NotebookUtils**. Use
> `import notebookutils` and call `notebookutils.*`. The old `mssparkutils` namespace
> remains backward compatible but is deprecated and will be retired; all new features
> ship only under `notebookutils`. NotebookUtils requires Spark 3.4 (Runtime v1.2) or above.

## Essential Imports
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, current_timestamp, year, month
from pyspark.sql.types import *
import notebookutils  # Current namespace (formerly mssparkutils)
```

## NotebookUtils

Available modules: `notebookutils.fs`, `notebookutils.notebook`, `notebookutils.credentials`,
`notebookutils.lakehouse`, `notebookutils.runtime`, `notebookutils.session`,
`notebookutils.udf`, `notebookutils.variableLibrary`.

Run `notebookutils.help()` for an overview, or `notebookutils.fs.help()` (etc.) per module.

### File System Operations
```python
import notebookutils

# List directory contents
notebookutils.fs.ls("Files/tmp")  # Relative path; in a Spark notebook this resolves to the default lakehouse
notebookutils.fs.ls("abfss://<container>@<account>.dfs.core.windows.net/<path>")

# View file properties
files = notebookutils.fs.ls('directory_path')
for file in files:
    print(file.name, file.isDir, file.isFile, file.path, file.size)

# Create directories (creates parents as needed)
notebookutils.fs.mkdirs("Files/<new_dir>")

# Copy files/directories
notebookutils.fs.cp('source', 'destination', recurse=True)  # recurse defaults to False

# Fast copy (azcopy) for large volumes
notebookutils.fs.fastcp('source', 'destination', recurse=True)  # recurse defaults to True

# Move files/directories: mv(src, dest, create_path, overwrite=False)
notebookutils.fs.mv('source', 'destination', create_path=True, overwrite=True)

# Preview file content: head(file, max_bytes=1024*100)
notebookutils.fs.head('file_path', 1024)

# Write a UTF-8 string to a file (last arg overwrites if True)
notebookutils.fs.put("file_path", "content", True)

# Append to a file (last arg creates the file if it doesn't exist)
notebookutils.fs.append("file_path", "content", True)

# Check existence (use before cp/mv/rm to avoid errors)
notebookutils.fs.exists("Files/data/input.csv")

# Delete files/directories
notebookutils.fs.rm('file_path', recurse=True)

# getProperties(path) -> map of metadata. Python notebooks only (not PySpark/Scala/R).
notebookutils.fs.getProperties("abfss://<container>@<account>.dfs.core.windows.net/<path>")
```

### Mount Operations
```python
# Mount a lakehouse or Fabric workspace storage with Microsoft Entra token (default, no creds)
notebookutils.fs.mount(
    "abfss://<workspace_name>@onelake.dfs.fabric.microsoft.com/<lakehouse_name>.Lakehouse",
    "/test"
)

# Mount ADLS Gen2 with account key (store the key in Key Vault, not in code)
accountKey = notebookutils.credentials.getSecret("<vaultURI>", "<secretName>")
notebookutils.fs.mount(
    "abfss://mycontainer@<accountname>.dfs.core.windows.net",
    "/test",
    {"accountKey": accountKey}
)

# Mount with SAS token
sasToken = notebookutils.credentials.getSecret("<vaultURI>", "<secretName>")
notebookutils.fs.mount(
    "abfss://mycontainer@<accountname>.dfs.core.windows.net",
    "/test",
    {"sasToken": sasToken}
)

# Optional tuning: extraConfigs supports fileCacheTimeout (default 120s; 0 = always latest) and timeout (default 30s)
notebookutils.fs.mount("abfss://...", "/test", {"fileCacheTimeout": 0, "timeout": 30})

# Access mounted files via the notebookutils.fs API
path = notebookutils.fs.getMountPath("/test")  # getMountPath(mountPoint, scope="")
notebookutils.fs.ls(f"file://{path}")

# Check existing mount points
notebookutils.fs.mounts()

# Unmount (NOT automatic: always call explicitly to release disk space)
notebookutils.fs.unmount("/test")
```

### Notebook Operations
```python
# Run another notebook: run(path, timeout_seconds=90, arguments=None, workspace="")
exitVal = notebookutils.notebook.run("NotebookName", 90, {"param": "value"})

# Run notebook in a different workspace (cross-workspace requires Runtime v1.2+)
exitVal = notebookutils.notebook.run("NotebookName", 90, {"param": "value"}, "workspace_id")

# Run multiple notebooks in parallel
notebookutils.notebook.runMultiple(["Notebook1", "Notebook2"])

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
            "retry": 1,
            "retryIntervalInSeconds": 10,
            "dependencies": ["NotebookSimple"]
        }
    ],
    "timeoutInSeconds": 43200,   # entire DAG; default 43200 (12h)
    "concurrency": 50            # default is 3x available CPU cores; 0 = unlimited
}

# Validate before running (catches duplicate names, missing deps, cycles)
notebookutils.notebook.validateDAG(DAG)

# runMultiple(dag, config=None) -> {activity_name: {"exitVal": str, "exception": err|None}}
results = notebookutils.notebook.runMultiple(DAG)

# Exit notebook with a value (always a string; don't call inside try/except)
notebookutils.notebook.exit("exit_value")
```

### Credentials & Security
```python
# Get Microsoft Entra access tokens: getToken(audience)
token = notebookutils.credentials.getToken('storage')   # Azure Storage (ADLS Gen2 / Blob)
token = notebookutils.credentials.getToken('pbi')       # Power BI / Fabric REST APIs
token = notebookutils.credentials.getToken('keyvault')  # Azure Key Vault
token = notebookutils.credentials.getToken('kusto')     # Synapse RTA KQL DB (ADX)

# Get secrets from Key Vault: getSecret(akvName, secret)
secret = notebookutils.credentials.getSecret('https://<keyvault>.vault.azure.net/', 'secret_name')

# Store a secret (Python/PySpark/R only, not public Scala API)
notebookutils.credentials.putSecret('https://<keyvault>.vault.azure.net/', 'secret_name', 'secret_value')
```

### Lakehouse Management
```python
# Create a lakehouse (optional schema support via create)
artifact = notebookutils.lakehouse.create("lakehouse_name", "Description", "workspace_id")

# Get a lakehouse (getWithProperties returns extended metadata + connection details)
artifact = notebookutils.lakehouse.get("lakehouse_name", "workspace_id")

# Update: update(name, newName, description, workspaceId)
updated = notebookutils.lakehouse.update("old_name", "new_name", "Updated description", "workspace_id")

# Delete -> Boolean
is_deleted = notebookutils.lakehouse.delete("lakehouse_name", "workspace_id")

# List lakehouses in a workspace
lakehouses = notebookutils.lakehouse.list("workspace_id")

# List tables in a lakehouse (workspaceId and maxResults optional)
tables = notebookutils.lakehouse.listTables("lakehouse_name", "workspace_id")
```

### Runtime Context
```python
# Read-only session context (a dict)
context = notebookutils.runtime.context
print(context['currentNotebookName'])
print(context['currentWorkspaceName'])
print(context['defaultLakehouseName'])

# Branch on execution mode
if context['isForPipeline']:
    print("Running in a pipeline")
elif context['isReferenceRun']:
    print("Running as a referenced notebook")
else:
    print("Interactive run")
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
from pyspark.sql.functions import col, to_timestamp, current_timestamp, year, month

# Add columns with current timestamp
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

# Write to a lakehouse Delta table (managed tables only in Fabric)
df.write.format("delta").mode("overwrite").saveAsTable("orders_processed")

# Overwrite with a schema change
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("orders_processed")
```

### Fabric Data Warehouse (Spark connector)
```python
# Required imports before using the connector (the connector ships in the Fabric runtime;
# no installation needed). Run these at the top of the notebook.
import com.microsoft.spark.fabric
from com.microsoft.spark.fabric.Constants import Constants

# Read from a warehouse / lakehouse SQL analytics endpoint (three-part name)
df = spark.read.synapsesql("<warehouse_or_lakehouse>.<schema>.<table_or_view>")

# Read with a custom T-SQL query
df = spark.read.option(Constants.DatabaseName, "<warehouse>").synapsesql("<T-SQL query>")

# Write to a warehouse table (write requires the GA runtime, Runtime 1.3+)
# Supported save modes: errorifexists (default), ignore, overwrite, append
df.write.mode("overwrite").synapsesql("<warehouse>.<schema>.<table>")
df.write.mode("append").synapsesql("<warehouse>.<schema>.<table>")
```

## Spark SQL Integration

### Using SQL Magic
```python
# In a notebook cell, use the %%sql magic
%%sql
SELECT * FROM salesorders LIMIT 1000
```

### Embedding SQL in PySpark
```python
# Create temporary view
df.createOrReplaceTempView("temp_orders")

# Execute SQL query
result_df = spark.sql("SELECT * FROM temp_orders WHERE amount > 100")

# Query lakehouse tables (use the fully qualified name lakehouse_name.table_name)
df = spark.sql("SELECT * FROM lakehouse_name.table_name LIMIT 1000")
```

## Display and Visualization
```python
# Rich, interactive table/chart view (Fabric built-in; chart config persists across reruns)
display(df)

# Basic show
df.show()
df.show(20)

# Collect data to driver (use with caution)
data = df.collect()

# Schema and stats
df.printSchema()
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
# Access default lakehouse files / tables
files = notebookutils.fs.ls("Files/")
tables = notebookutils.fs.ls("Tables/")

# Read from a lakehouse Delta table
df = spark.read.format("delta").load("Tables/table_name")
```

### OneLake Integration
```python
# Access OneLake paths (global endpoint only: regional endpoints are not supported)
onelake_path = "abfss://<workspace_id>@onelake.dfs.fabric.microsoft.com/<lakehouse_id>/Files/"
df = spark.read.parquet(onelake_path + "data.parquet")
```

### V-Order and Optimize Write
```python
# V-Order is disabled by default in new Fabric workspaces (write-heavy default).
# Enable it for read-heavy / Direct Lake / Warehouse-consumed (gold) tables.
spark.conf.set("spark.sql.parquet.vorder.default", "true")   # session-level
spark.conf.get("spark.sql.parquet.vorder.default")           # check current value

# Optimize Write (fewer, larger files)
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
```
```sql
-- Table-level V-Order (affects future writes only)
%%sql
ALTER TABLE person SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "true");

-- Compact and (re)apply V-Order + Z-Order in one command
OPTIMIZE myTable WHERE date >= '2025-01-01' ZORDER BY (customer_id) VORDER;
```
> In Runtime 1.3+ the older `spark.sql.parquet.vorder.enable` setting was removed;
> use `spark.sql.parquet.vorder.default` (or resource profiles like `readHeavyForSpark`).

### Variable Library
```python
# Read centrally managed variables from a Variable Library item
notebookutils.variableLibrary.help()
value = notebookutils.variableLibrary.get("$(/**/<library_name>/<variable_name>)")
```

### Semantic Link (SemPy)
```python
# Semantic link is preinstalled in Runtime 1.2 (Spark 3.4) and above.
# Upgrade with: %pip install -U semantic-link
import sempy.fabric as fabric

# Read a Power BI semantic model table into a FabricDataFrame
df = fabric.read_table("<dataset_name>", "<table_name>")

# Evaluate a DAX query
df_dax = fabric.evaluate_dax("<dataset_name>", "EVALUATE <table_or_expression>")

# Evaluate a measure
df_measure = fabric.evaluate_measure("<dataset_name>", "<measure_name>")
```
```python
# %%dax cell magic (load once with %load_ext sempy); result is captured in `_`
%load_ext sempy
```

### Notebook Resources
```python
# Path to the notebook's built-in resource folder (use in referenced notebooks too)
resource_path = notebookutils.nbResPath
config_df = spark.read.json(f"{resource_path}/config.json")
```

This cheatsheet covers the most commonly used PySpark operations in Microsoft Fabric, based on verified code examples from Microsoft's official documentation.
