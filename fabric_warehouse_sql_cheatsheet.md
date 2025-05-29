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
-- Create and populate table from another table
SELECT * INTO AWDW.dbo.dim_currency FROM AdventureWorksLakehouse.dbo.dim_currency;
```

### Altering Tables

#### Supported ALTER TABLE Operations
Currently, only the following subset of ALTER TABLE operations in Warehouse in Microsoft Fabric are supported:
- ADD nullable columns of supported column data types.
- DROP COLUMN
- ADD or DROP PRIMARY KEY, UNIQUE, and FOREIGN_KEY column constraints, but only if the NOT ENFORCED option has been specified.

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

### TRUNCATE TABLE
TRUNCATE TABLE is supported in Warehouse in Microsoft Fabric.

```sql
TRUNCATE TABLE [dbo].[table_name];
```

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

Microsoft Fabric supports the most commonly used T-SQL data types.

### Commonly Supported Data Types
- **Numeric**: `INT`, `BIGINT`, `SMALLINT`, `TINYINT`, `DECIMAL`, `NUMERIC`, `FLOAT`, `REAL`
- **Character**: `VARCHAR`, `NVARCHAR`, `CHAR`, `NCHAR`
- **Date/Time**: `DATE`, `TIME`, `DATETIME`, `DATETIME2`, `SMALLDATETIME`
- **Binary**: `BINARY`, `VARBINARY`
- **Other**: `BIT`, `UNIQUEIDENTIFIER`

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
- `BULK LOAD`
- `CREATE USER`
- `FOR JSON` (must be last operator, not allowed in subqueries)
- `IDENTITY` Columns
- Manually created multi-column stats
- Materialized views
- `MERGE`
- `PREDICT`
- Queries targeting system and user tables
- Recursive queries
- Result Set Caching
- `SELECT FOR XML`
- `SET ROWCOUNT`
- `SET TRANSACTION ISOLATION LEVEL`
- `sp_showspaceused`
- Triggers

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
- Use Azure Data Studio
- Connect through the Fabric portal web interface
- Utilize REST APIs for programmatic access

This cheatsheet covers the core T-SQL functionality available in Microsoft Fabric Warehouse based on official Microsoft documentation and verified code examples.