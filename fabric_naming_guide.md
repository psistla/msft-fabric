# Microsoft Fabric Data Analytics Naming Standards Guide

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Foundation Principles](#foundation-principles)
3. [Core Naming Components](#core-naming-components)
4. [Workspace Naming Standards](#workspace-naming-standards)
5. [Workload-Specific Naming Conventions](#workload-specific-naming-conventions)
6. [Implementation Guidelines](#implementation-guidelines)
7. [Governance and Compliance](#governance-and-compliance)
8. [Examples and Templates](#examples-and-templates)

## Executive Summary

This guide establishes comprehensive naming standards for Microsoft Fabric Data Analytics implementations across all workloads. These standards ensure consistency, discoverability, and maintainability of data assets while supporting both technical and business users.

### Key Benefits
- **Consistency**: Uniform approach across all Fabric experiences
- **Discoverability**: Easy identification and location of artifacts
- **Maintainability**: Clear lineage and dependencies
- **Governance**: Simplified compliance and security management
- **Collaboration**: Enhanced teamwork between different personas

## Foundation Principles

### 1. Universal Constraints
Based on the most restrictive Fabric artifacts (Lakehouses), all naming conventions must adhere to:
- **Alphanumeric characters and underscores only**
- **First character must be a letter**
- **No spaces or special characters (except underscore)**
- **Case considerations**: Use consistent casing (recommended: lowercase with proper noun capitalization)

### 2. Core Philosophy
- **Descriptive**: Names should clearly indicate purpose and content
- **Hierarchical**: Support logical grouping and sorting
- **Scalable**: Accommodate future growth and changes
- **Business-Friendly**: Balance technical precision with user accessibility

## Core Naming Components

### Standard Format Structure
```
{Experience}_{ArtifactType}_{Index}_{Stage}_{Description}_{Suffix}
```

### Component Definitions

#### Experience Prefixes
| Experience | Abbreviation | Description |
|------------|--------------|-------------|
| Power BI | PBI | Business intelligence and reporting |
| Data Factory | DF | Data integration and orchestration |
| Synapse Data Engineering | DE | Big data processing and engineering |
| Synapse Data Science | DS | Machine learning and analytics |
| Synapse Data Warehouse | DW | Enterprise data warehousing |
| Synapse Real-Time Analytics | RTA | Streaming and real-time analytics |
| Data Activator | DA | Event-driven automation |

#### Artifact Type Abbreviations
| Experience | Artifact | Abbreviation |
|------------|----------|--------------|
| **Power BI** | Dataset | DS |
| | Dataflow | DFL |
| | Datamart | DM |
| | Report | RPT |
| | Dashboard | DASH |
| | Paginated Report | PRPT |
| **Data Factory** | Pipeline | PL |
| | Dataflow Gen2 | DFL |
| **Data Engineering** | Lakehouse | LH |
| | Notebook | NB |
| | Spark Job Definition | SJ |
| **Data Science** | Model | MDL |
| | Experiment | EXP |
| | Notebook | NB |
| **Data Warehouse** | Warehouse | WH |
| **Real-Time Analytics** | KQL Database | DB |
| | KQL Queryset | QS |
| | Eventstream | ES |

#### Index Numbering
- **Purpose**: Control execution order and logical grouping
- **Format**: Three-digit numbers (100, 200, 300)
- **Benefits**: Allows insertion of intermediate steps without renaming

#### Stage Identifiers
| Stage | Description | Use Case |
|-------|-------------|----------|
| RAW | Unprocessed source data | Initial ingestion |
| BRONZE | Basic cleansing and validation | Data lake bronze layer |
| SILVER | Transformed and integrated | Data lake silver layer |
| GOLD | Business-ready, aggregated | Data lake gold layer |
| STAGING | Temporary processing area | ETL intermediate steps |
| PROD | Production-ready assets | Final deployment |
| DEV | Development environment | Testing and development |
| UAT | User acceptance testing | Pre-production validation |

## Workspace Naming Standards

### Workspace Naming Convention
```
{Environment}_{BusinessDomain}_{Purpose}_{Region}
```

### Environment Identifiers
- **DEV**: Development workspace
- **TST**: Testing workspace
- **UAT**: User acceptance testing
- **PRD**: Production workspace

### Examples
- `PRD_Sales_Analytics_EastUS`
- `DEV_Finance_DataEngineering_WestEU`
- `UAT_Marketing_ML_CentralUS`

## Workload-Specific Naming Conventions

### Data Factory Workload

#### Pipeline Naming
```
DF_PL_{Index}_{Stage}_{SourceToTarget}_{ProcessType}
```

**Examples:**
- `DF_PL_100_BRONZE_SalesForceToLake_Extract`
- `DF_PL_200_SILVER_LakeToWarehouse_Transform`
- `DF_PL_300_GOLD_WarehouseToMart_Load`

#### Dataflow Gen2 Naming
```
DF_DFL_{Index}_{Stage}_{DataDomain}_{Transformation}
```

**Examples:**
- `DF_DFL_100_BRONZE_Customer_Cleansing`
- `DF_DFL_200_SILVER_Product_Enrichment`

### Data Engineering Workload

#### Lakehouse Naming
```
DE_LH_{Index}_{Stage}_{DataDomain}
```

**Examples:**
- `DE_LH_100_BRONZE_WideWorldImporters`
- `DE_LH_200_SILVER_CustomerData`
- `DE_LH_300_GOLD_SalesAnalytics`

#### Notebook Naming
```
DE_NB_{Index}_{Stage}_{Purpose}_{ProcessType}
```

**Examples:**
- `DE_NB_100_BRONZE_DataIngestion_Streaming`
- `DE_NB_200_SILVER_DataTransformation_Batch`
- `DE_NB_300_GOLD_DataAggregation_Scheduled`

#### Spark Job Definition Naming
```
DE_SJ_{Index}_{Stage}_{Purpose}_{Schedule}
```

**Examples:**
- `DE_SJ_100_SILVER_CustomerETL_Daily`
- `DE_SJ_200_GOLD_SalesReporting_Hourly`

### Data Warehouse Workload

#### Warehouse Naming
```
DW_WH_{Stage}_{BusinessDomain}_{Purpose}
```

**Examples:**
- `DW_WH_GOLD_Sales_Analytics`
- `DW_WH_SILVER_Finance_Reporting`
- `DW_WH_PROD_Enterprise_DataMart`

### Data Science Workload

#### Experiment Naming
```
DS_EXP_{UseCase}_{Version}
```

**Examples:**
- `DS_EXP_CustomerChurn_V1`
- `DS_EXP_PricePrediction_V2`
- `DS_EXP_FraudDetection_V1`

#### Model Naming
```
DS_MDL_{UseCase}_{Algorithm}_{Version}
```

**Algorithm Abbreviations:**
| Algorithm | Abbreviation |
|-----------|--------------|
| Decision Tree | DT |
| Random Forest | RF |
| Logistic Regression | LOR |
| Linear Regression | LIR |
| Support Vector Machines | SVM |
| K Nearest Neighbours | KNN |
| XGBoost | XGB |
| Light GBM | LGBM |
| Neural Network | NN |

**Examples:**
- `DS_MDL_CustomerChurn_RF_V1`
- `DS_MDL_PricePrediction_XGB_V2`
- `DS_MDL_FraudDetection_NN_V1`

#### Data Science Notebook Naming
```
DS_NB_{UseCase}_{Purpose}_{Version}
```

**Examples:**
- `DS_NB_CustomerChurn_FeatureEngineering_V1`
- `DS_NB_PricePrediction_HyperparameterTuning_V2`
- `DS_NB_FraudDetection_ModelTraining_V1`

### Real-Time Analytics Workload

#### KQL Database Naming
```
RTA_DB_{DataSource}_{Purpose}_{Region}
```

**Examples:**
- `RTA_DB_IoTSensors_Monitoring_EastUS`
- `RTA_DB_WebLogs_Analytics_WestEU`
- `RTA_DB_AppTelemetry_Observability_CentralUS`

#### Eventstream Naming
```
RTA_ES_{Source}_{Destination}_{EventType}
```

**Examples:**
- `RTA_ES_IoTHub_KQLDatabase_SensorData`
- `RTA_ES_EventHub_Lakehouse_WebEvents`
- `RTA_ES_ServiceBus_Warehouse_TransactionData`

#### KQL Queryset Naming
```
RTA_QS_{BusinessDomain}_{AnalysisType}_{Purpose}
```

**Examples:**
- `RTA_QS_Operations_Performance_Monitoring`
- `RTA_QS_Security_Threat_Detection`
- `RTA_QS_Business_Customer_Analytics`

### Power BI Workload

#### Dataset Naming
For enterprise/shared datasets:
```
PBI_DS_{BusinessDomain}_{DataGranularity}
```

**Examples:**
- `PBI_DS_Sales_Daily`
- `PBI_DS_Finance_Monthly`
- `PBI_DS_Operations_Realtime`

#### Dataflow Naming
```
PBI_DFL_{BusinessDomain}_{Purpose}_{RefreshFrequency}
```

**Examples:**
- `PBI_DFL_Sales_CustomerMaster_Daily`
- `PBI_DFL_Finance_BudgetData_Monthly`
- `PBI_DFL_HR_EmployeeData_Weekly`

#### Report and Dashboard Naming
Business-friendly names without technical prefixes:
- Reports: Use descriptive business names (e.g., "Weekly Sales Performance", "Customer Satisfaction Dashboard")
- Dashboards: Focus on audience and purpose (e.g., "Executive Summary", "Operations Monitor")

## Implementation Guidelines

### 1. Phased Approach

#### Phase 1: Core Infrastructure
- Establish workspace naming standards
- Implement naming for shared/enterprise assets
- Create governance documentation

#### Phase 2: Workload-Specific Standards
- Deploy naming conventions per workload
- Train teams on standards
- Implement validation processes

#### Phase 3: Enforcement and Monitoring
- Automated naming validation
- Regular compliance audits
- Continuous improvement

### 2. Team Responsibilities

#### Data Engineering Team
- Implement naming standards for all DE artifacts
- Maintain lakehouse and notebook naming consistency
- Document data lineage using standardized names

#### Data Science Team
- Follow experiment and model naming conventions
- Maintain version control through naming
- Document algorithm choices in artifact names

#### Analytics Team
- Apply standards to warehouse and BI artifacts
- Balance technical naming with business usability
- Maintain report and dataset naming consistency

#### Data Factory Team
- Implement pipeline and dataflow naming standards
- Maintain processing order through index numbering
- Document data movement through standardized names

### 3. Exception Handling

#### Business-Facing Artifacts
- Reports and dashboards may use business-friendly names
- Apps and public content prioritize user experience
- Maintain mapping between technical and business names

#### Legacy Asset Integration
- Gradual migration approach for existing assets
- Document mapping between old and new naming conventions
- Maintain backward compatibility during transition

## Governance and Compliance

### 1. Naming Policy Enforcement

#### Automated Validation
- Implement naming validation in CI/CD pipelines
- Use Azure Policy or custom solutions for enforcement
- Regular automated compliance reporting

#### Manual Review Process
- Peer review for new artifact creation
- Regular audit cycles
- Exception approval workflow

### 2. Documentation Requirements

#### Artifact Documentation
- Purpose and business justification
- Data lineage and dependencies
- Ownership and contact information
- Refresh schedules and SLAs

#### Change Management
- Impact assessment for naming changes
- Communication plan for affected stakeholders
- Migration timeline and rollback procedures

### 3. Training and Adoption

#### Initial Training
- Comprehensive naming standards workshop
- Role-specific implementation guides
- Hands-on practice sessions

#### Ongoing Support
- Regular refresher training
- New team member onboarding
- Community of practice forums

## Examples and Templates

### Complete Naming Examples

#### Data Lakehouse Architecture
```
DE_LH_100_BRONZE_CustomerData
DE_LH_200_SILVER_CustomerData
DE_LH_300_GOLD_CustomerAnalytics

DF_PL_100_BRONZE_CRMToLakehouse_Extract
DF_PL_200_SILVER_BronzeToSilver_Transform
DF_PL_300_GOLD_SilverToGold_Aggregate

DE_NB_150_BRONZE_DataQuality_Validation
DE_NB_250_SILVER_BusinessRules_Application
DE_NB_350_GOLD_MetricsCalculation_Batch
```

#### Machine Learning Pipeline
```
DS_EXP_CustomerLifetimeValue_V1
DS_NB_CustomerLifetimeValue_DataPreparation_V1
DS_NB_CustomerLifetimeValue_FeatureEngineering_V1
DS_NB_CustomerLifetimeValue_ModelTraining_V1
DS_MDL_CustomerLifetimeValue_XGB_V1
```

#### Real-Time Analytics Solution
```
RTA_ES_WebEvents_KQLDatabase_ClickStream
RTA_DB_UserBehavior_Analytics_EastUS
RTA_QS_Marketing_UserJourney_Analysis
```

### Naming Templates

#### Template: Data Pipeline Series
```
DF_PL_{100+}_{STAGE}_{SourceSystem}To{TargetSystem}_{ProcessType}
```

#### Template: Medallion Architecture
```
{Experience}_{Artifact}_{100|200|300}_{BRONZE|SILVER|GOLD}_{DataDomain}
```

#### Template: ML Model Lifecycle
```
DS_EXP_{UseCase}_{Version}
DS_NB_{UseCase}_{MLPhase}_{Version}
DS_MDL_{UseCase}_{Algorithm}_{Version}
```

## Conclusion

This comprehensive naming standards guide provides the foundation for consistent, discoverable, and maintainable Microsoft Fabric implementations. Regular review and updates of these standards ensure they continue to meet evolving business and technical requirements.

### Success Metrics
- **Artifact Discoverability**: Time to find relevant data assets
- **Development Efficiency**: Reduced time for onboarding and development
- **Governance Compliance**: Percentage of assets following standards
- **User Satisfaction**: Feedback from business and technical users

### Next Steps
1. Review and customize standards for your organization
2. Conduct pilot implementation with core team
3. Develop training materials and documentation
4. Implement governance and enforcement mechanisms
5. Monitor adoption and gather feedback for continuous improvement

---

*This guide is based on Microsoft Learn documentation, Azure Cloud Adoption Framework best practices, and industry-verified implementations as of May 2025.*