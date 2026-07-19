# Microsoft Fabric Warehouse SQL Cheatsheet

## Overview
Microsoft Fabric Data Warehouse is a next-generation data warehousing solution within Microsoft Fabric. The lake-centric warehouse is built on an enterprise grade distributed processing engine that enables industry leading performance at scale while minimizing the need for configuration and management.

## Key Differences: Warehouse vs SQL Analytics Endpoint
- **Warehouse**: Creating, altering, and dropping tables, and insert, update, and delete are only supported in Warehouse in Microsoft Fabric, not in the SQL analytics endpoint of the Lakehouse
- **SQL Analytics Endpoint**: Read-only queries, can create views, functions, and procedures

---

## Table Operations

### Creating Tables

#### Basic CREATE TABLE Syntax
```sql
CREATE TABLE [schema_name].[table_name] (
    column1 datatype [constraints],
    column2 datatype [constraints],
    ...
);
```

#### Create Table with Primary Key
```sql
CREATE TABLE [dbo].[dimension_city] (
    [CityKey] INT NOT NULL,
    [WWICityID] INT NOT NULL,
    [City] VARCHAR(50) NOT NULL,
    [StateProvince] VARCHAR(50) NOT NULL,
    [Country] VARCHAR(60) NOT NULL
    CONSTRAINT [PK_dimension_city] PRIMARY KEY NONCLUSTERED ([CityKey]) NOT ENFORCED
);
```

#### Create Table As Select (CTAS)
```sql
-- CREATE TABLE AS SELECT (CTAS): create and populate a new table from a query
CREATE TABLE [dbo].[dim_currency]
AS
SELECT * FROM AdventureWorksLakehouse.dbo.dim_currency;

-- SELECT ... INTO is also supported
SELECT * INTO AWDW.dbo.dim_currency FROM AdventureWorksLakehouse.dbo.dim_currency;
```

#### Clone Table (Zero-Copy Clone)
`CREATE TABLE ... AS CLONE OF` creates a near-instantaneous zero-copy clone. Only metadata is copied; the underlying Parquet data files are shared. You can clone as of the current state or a past point in time (within the configured data retention period).

```sql
-- Clone a table as of its current state
CREATE TABLE [dbo].[dimension_city_clone]
AS CLONE OF [dbo].[dimension_city];

-- Clone a table as of a past point in time (UTC)
CREATE TABLE [dbo].[dimension_city_clone]
AS CLONE OF [dbo].[dimension_city] AT '2026-07-01T09:00:00';
```

### Altering Tables

#### Supported ALTER TABLE Operations
Currently, only the following subset of ALTER TABLE operations in Warehouse in Microsoft Fabric are supported:
- ADD nullable columns of supported column data types.
- DROP COLUMN
- ADD or DROP PRIMARY KEY, UNIQUE, and FOREIGN_KEY column constraints, but only if the NOT ENFORCED option has been specified.
- ALTER TABLE on distributed (session-scoped) temporary tables.
- ALTER TABLE ... ALTER COLUMN (preview).
- Supported ALTER TABLE statements can be executed inside an explicit user-defined transaction.

All other ALTER TABLE operations are blocked.

```sql
-- Add nullable column
ALTER TABLE [dbo].[table_name] 
ADD [new_column] VARCHAR(50) NULL;

-- Drop column
ALTER TABLE [dbo].[table_name] 
DROP COLUMN [column_name];

-- Add primary key constraint (NOT ENFORCED)
ALTER TABLE [dbo].[table_name]
ADD CONSTRAINT [PK_table_name] PRIMARY KEY NONCLUSTERED ([column_name]) NOT ENFORCED;
```

### Dropping Tables
```sql
-- Drop table if exists
DROP TABLE IF EXISTS [dbo].[table_name];
```

---

## Data Manipulation

### INSERT Operations

#### Basic INSERT
```sql
INSERT INTO [dbo].[table_name] (column1, column2, column3)
VALUES (value1, value2, value3);
```

#### INSERT with SELECT
INSERT INTO [dbo].[bing_covid-19_data_2023] SELECT * FROM [dbo].[bing_covid-19_data] WHERE [updated] > '2023-02-28';

#### INSERT from Cross-Database Query
Using three-part naming to reference the database and tables, you can insert data from one database to another. INSERT INTO ContosoWarehouse.dbo.Affiliation SELECT * FROM My_Lakehouse.dbo.Affiliation;

### UPDATE Operations
```sql
UPDATE [dbo].[table_name]
SET column1 = value1, column2 = value2
WHERE condition;
```

### DELETE Operations
```sql
DELETE FROM [dbo].[table_name]
WHERE condition;
```

### MERGE Operations
MERGE syntax is supported and is a generally available (GA) feature in Warehouse in Microsoft Fabric. It performs INSERT, UPDATE, and DELETE operations on a target table based on the results of a join with a source table, all in a single statement.

```sql
MERGE INTO [dbo].[target_table] AS target
USING [dbo].[source_table] AS source
    ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET target.value = source.value
WHEN NOT MATCHED BY TARGET THEN
    INSERT (id, value) VALUES (source.id, source.value)
WHEN NOT MATCHED BY SOURCE THEN
    DELETE;
```

### TRUNCATE TABLE
TRUNCATE TABLE is supported in Warehouse in Microsoft Fabric.

```sql
TRUNCATE TABLE [dbo].[table_name];
```

---

## Data Ingestion

### COPY INTO
The `COPY INTO` T-SQL statement is the primary high-throughput mechanism for ingesting external files into a Warehouse table. It currently supports CSV, JSONL, and PARQUET file formats. Supported data sources are Azure Data Lake Storage (ADLS) Gen2 and Azure Blob Storage (reading directly from OneLake paths is in preview).

```sql
COPY INTO [dbo].[table_name]
FROM 'https://<storage_account>.dfs.core.windows.net/<container>/<folder>/'
WITH (
    FILE_TYPE = 'PARQUET'
);
```

### OPENROWSET
The `OPENROWSET(BULK ...)` function reads the contents of Parquet, CSV, or JSONL files directly, returning them as a set of rows without ingesting them first. Files can be in Azure Blob Storage, ADLS Gen2, or Fabric OneLake (OneLake source is in preview). The schema is inferred automatically, or can be defined explicitly with a `WITH` clause.

```sql
-- Explore a file's contents directly
SELECT TOP 10 *
FROM OPENROWSET(BULK 'https://<storage_account>.blob.core.windows.net/<container>/<file>.parquet') AS data;

-- Create and populate a table from an external file
CREATE TABLE [dbo].[table_name]
AS
SELECT *
FROM OPENROWSET(BULK 'https://<storage_account>.blob.core.windows.net/<container>/<file>.parquet') AS data;

-- Explicit schema with the WITH clause
SELECT *
FROM OPENROWSET(BULK 'https://<storage_account>.blob.core.windows.net/<container>/<file>.parquet')
WITH (
    Column1 INT,
    Column2 VARCHAR(20)
) AS data;
```

> `bcp` client-side bulk copy (bcp.exe, `SqlBulkCopy`, `SQLServerBulkCopy`) is supported as a preview feature. Pipelines and dataflows are also available for ingestion.

---

## Query Operations

### Basic SELECT
```sql
-- Select top 100 rows
SELECT TOP 100 * FROM [dbo].[table_name];

-- Select with WHERE clause
SELECT column1, column2, column3
FROM [dbo].[table_name]
WHERE condition;
```

### Common Table Expressions (CTEs)
Fabric Warehouse and SQL analytics endpoint both support standard, sequential, and nested CTEs. While CTEs are generally available in Microsoft Fabric, nested CTEs are currently a preview feature.

```sql
-- Standard CTE
WITH cte_name AS (
    SELECT column1, column2
    FROM [dbo].[table_name]
    WHERE condition
)
SELECT * FROM cte_name;

-- Sequential CTE
WITH cte1 AS (
    SELECT column1, column2 FROM [dbo].[table1]
),
cte2 AS (
    SELECT column3, column4 FROM [dbo].[table2]
)
SELECT * FROM cte1 
INNER JOIN cte2 ON cte1.column1 = cte2.column3;
```

### Cross-Database Queries
```sql
-- Query across databases using three-part naming
SELECT w.column1, l.column2
FROM ContosoWarehouse.dbo.table1 w
INNER JOIN My_Lakehouse.dbo.table2 l ON w.id = l.id;
```

### Time Travel (Query Data as of a Past Point in Time)
Warehouse and the SQL analytics endpoint support querying historical data using the `OPTION (FOR TIMESTAMP AS OF ...)` query hint (preview). The timestamp is in UTC and uses the format `YYYY-MM-DDTHH:MM:SS[.fff]`. The hint applies to the entire statement (including all joined warehouse tables) and can be used once per SELECT. Time travel is limited to the configured data retention period (default 30 calendar days).

```sql
-- Read a table as it existed at a past point in time (UTC)
SELECT *
FROM [dbo].[dimension_customer]
OPTION (FOR TIMESTAMP AS OF '2026-07-01T20:44:13.700');
```

Time-travel results are read-only for a plain `SELECT`, but the `OPTION` clause can also be combined with DML such as `INSERT INTO ... SELECT`, `CREATE TABLE AS SELECT` (CTAS), and `SELECT ... INTO`.

---

## Schema Management

### Creating Custom Schemas
Warehouse supports the creation of custom schemas. Like in SQL Server, schemas are a good way to group together objects that are used in a similar fashion. Schema names are case sensitive. Schema names can't contain / or \ or end with a .

```sql
-- Create custom schema
CREATE SCHEMA [wwi];

-- Create table in custom schema
CREATE TABLE [wwi].[products] (
    [ProductID] INT NOT NULL,
    [ProductName] VARCHAR(100) NOT NULL
);
```

---

## Stored Procedures and Functions

### Creating Views
```sql
CREATE VIEW [dbo].[view_name] AS
SELECT column1, column2, column3
FROM [dbo].[table_name]
WHERE condition;
```

### Creating Functions
```sql
CREATE FUNCTION [dbo].[function_name](@parameter datatype)
RETURNS datatype
AS
BEGIN
    DECLARE @result datatype;
    -- Function logic here
    RETURN @result;
END;
```

### Creating Stored Procedures
```sql
CREATE PROCEDURE [dbo].[procedure_name]
    @param1 datatype,
    @param2 datatype
AS
BEGIN
    -- Procedure logic here
END;
```

---

## Temporary Tables

### Session-Scoped Temporary Tables
Session-scoped distributed #temp tables are supported in Warehouse in Microsoft Fabric. Session-scoped temporary (#temp) tables can be created in Fabric Data Warehouse. These tables exist only within the session in which they are created.

```sql
-- Create temporary table
CREATE TABLE #temp_table (
    column1 INT,
    column2 VARCHAR(50)
);

-- Insert data into temp table
INSERT INTO #temp_table VALUES (1, 'Test');

-- Query temp table
SELECT * FROM #temp_table;
```

---

## Data Types

Warehouse supports a subset of T-SQL data types for persisted storage (tables and other persisted objects). Some unsupported types can still be used in queries, variables, parameters, and stored procedure logic.

### Supported Data Types (for tables)
- **Exact numerics**: `BIT`, `SMALLINT`, `INT`, `BIGINT`, `DECIMAL`/`NUMERIC`
- **Approximate numerics**: `FLOAT`, `REAL`
- **Date and time**: `DATE`, `TIME`, `DATETIME2` (precision limited to 6 digits of fractional seconds)
- **Character strings**: `CHAR`, `VARCHAR` (the storage limit for `VARCHAR(MAX)` is currently 16 MB)
- **Binary**: `VARBINARY` (the storage limit for `VARBINARY(MAX)` is currently 16 MB)
- **Other**: `UNIQUEIDENTIFIER` (stored as binary; its values can't be read on the SQL analytics endpoint)

### Notable Unsupported Data Types (for tables)
These types are not supported for persisted storage; use the listed alternatives:
- `TINYINT` -> use `SMALLINT`
- `MONEY` / `SMALLMONEY` -> use `DECIMAL`
- `DATETIME` / `SMALLDATETIME` -> use `DATETIME2`
- `DATETIMEOFFSET` -> use `DATETIME2` (convert with `AT TIME ZONE`)
- `NCHAR` / `NVARCHAR` -> use `CHAR` / `VARCHAR` (UTF-8 collation)
- `TEXT` / `NTEXT` / `JSON` -> use `VARCHAR`
- `IMAGE` -> use `VARBINARY`
- `XML`, CLR user-defined types, `GEOGRAPHY`/`GEOMETRY`, and the `VECTOR` type are not supported.

---

## Constraints and Keys

### Primary Keys
```sql
-- Add primary key during table creation
CREATE TABLE [dbo].[table_name] (
    [ID] INT NOT NULL,
    [Name] VARCHAR(50) NOT NULL,
    CONSTRAINT [PK_table_name] PRIMARY KEY NONCLUSTERED ([ID]) NOT ENFORCED
);
```

### Foreign Keys
```sql
-- Add foreign key constraint
ALTER TABLE [dbo].[child_table]
ADD CONSTRAINT [FK_child_parent] 
FOREIGN KEY ([parent_id]) REFERENCES [dbo].[parent_table]([id]) NOT ENFORCED;
```

### Unique Constraints
```sql
-- Add unique constraint
ALTER TABLE [dbo].[table_name]
ADD CONSTRAINT [UQ_table_column] UNIQUE NONCLUSTERED ([column_name]) NOT ENFORCED;
```

### IDENTITY Columns (Preview)
IDENTITY columns are supported (preview) and are commonly used to generate surrogate keys. Note the following behavior, which differs from SQL Server:
- Only the `BIGINT` data type is supported for IDENTITY columns.
- `IDENTITY_INSERT` is not supported; you can't manually insert or update identity column values.
- Defining a `seed` and `increment` (and therefore reseeding) is not supported.
- Adding a new IDENTITY column to an existing table with `ALTER TABLE` is not supported. Use CTAS or `SELECT ... INTO` instead.
- Generated values are guaranteed unique but can have gaps and are not necessarily sequential/ordered.

```sql
CREATE TABLE [dbo].[Trip] (
    TripID BIGINT IDENTITY,
    DateID INT,
    MedallionID INT
);
```

---

## Utility Commands

### Column Renaming
To change the name of the column in a user table in Warehouse, use the sp_rename stored procedure.

```sql
EXEC sp_rename 'table_name.old_column_name', 'new_column_name', 'COLUMN';
```

### Information Queries
```sql
-- Get table information
SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';

-- Get column information
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'your_table_name';
```

---

## Limitations and Unsupported Features

At this time, the following list of commands is NOT currently supported:

### Currently NOT Supported
- `BULK LOAD` (though `bcp` is supported as a preview feature)
- `CREATE USER`
- `FOR JSON` (must be the last operator in the query, so it's not allowed inside subqueries)
- Manually created multi-column stats
- Materialized views
- `PREDICT`
- Queries targeting system and user tables
- Recursive queries
- `SELECT` - `FOR XML`
- `SET ROWCOUNT`
- `SET TRANSACTION ISOLATION LEVEL`
- `sp_showspaceused`
- Synonyms
- Triggers
- Vector data type and search functions

> Note: Several items previously listed as unsupported are now available - `MERGE` (GA), `IDENTITY` columns (preview), and result set caching are all supported.

### Naming Restrictions
Schema and table names can't contain / or \

---

## Best Practices

1. **Use Three-Part Naming** for cross-database queries: `DatabaseName.SchemaName.TableName`

2. **Leverage CTEs** for complex queries instead of subqueries when possible

3. **Create Custom Schemas** to organize related objects logically

4. **Use NOT ENFORCED Constraints** for referential integrity documentation without performance impact

5. **Utilize Temporary Tables** for intermediate processing within sessions

6. **Consider Performance** - the distributed processing engine optimizes automatically, but efficient query design still matters

---

## Connection and Access

- Connect using SQL Server Management Studio (SSMS)
- Use the MSSQL extension for Visual Studio Code
- Use the web SQL query editor and visual query editor in the Fabric portal
- Utilize REST APIs for programmatic access

This cheatsheet covers the core T-SQL functionality available in Microsoft Fabric Warehouse based on official Microsoft documentation and verified code examples.