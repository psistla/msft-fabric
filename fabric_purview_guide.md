# Microsoft Purview and Fabric Security & Governance Integration Guide

## Overview

Microsoft Purview extends Microsoft Fabric's native security capabilities by providing comprehensive data governance, risk management, and compliance solutions. This integration delivers a unified approach to data protection across the entire Microsoft Intelligent Data Platform.

## 1. Microsoft Purview Architecture with Fabric

### Unified Data Governance Platform
Microsoft Purview is a family of data governance, risk, and compliance solutions that includes:
- **Risk and Compliance Solutions**: Microsoft 365 compliance capabilities
- **Unified Data Governance Solutions**: Microsoft Purview data governance, delivered through two solutions — the **Data Map** and the **Unified Catalog** (the former standalone "Azure Purview" governance portal has been consolidated into the unified Microsoft Purview portal)
- **Cross-Platform Coverage**: Microsoft 365, on-premises, multicloud, and SaaS data services

### Integration Benefits
With Microsoft Purview and Microsoft Fabric together, organizations can:
- Protect sensitive data across clouds, apps, and devices
- Identify data risks and manage regulatory compliance requirements
- Create an up-to-date map of the entire data estate with data classification and end-to-end lineage
- Identify where sensitive data is stored across the estate
- Create a secure environment for data consumers to find valuable data
- Generate insights about how data is stored and used

## 2. Core Purview Integration Components

### Microsoft Purview Unified Catalog and Data Map
**Automatic Metadata Discovery**:
- Automatically view metadata about Microsoft Fabric items in the Microsoft Purview Unified Catalog
- Live view integration for real-time visibility (same-tenant scenarios)
- Support for same-tenant and cross-tenant catalog connections (registered/scanned via the Data Map)
- Complete data lineage from source to Power BI reports
- Publication workflows for data products and glossary terms; data quality checks can be applied to ungoverned Fabric assets

**Data Asset Management**:
- Centralized catalog of all Fabric assets
- Automated discovery and classification of data assets
- Business glossary integration for consistent terminology
- Data stewardship workflows for governance accountability

### Microsoft Purview Information Protection
**Sensitivity Labels for Fabric**:
- Discover, classify, and protect Fabric data using sensitivity labels
- Sensitivity labels can be set on all Fabric items
- Label-based protection persists when data is exported via supported export paths (label/protection inheritance on export is currently supported for Power BI items only; other Fabric export paths issue a warning but don't carry the label)
- Automatic label application via default labels, downstream inheritance, inheritance from data sources, and programmatic (Power BI admin REST API) labeling; Data Map scans can also auto-assign labels based on classification rules
- Access to Fabric items can be controlled with sensitivity labels through Microsoft Purview **protection policies**

**Label Hierarchy and Policies**:
```
Sensitivity Label Structure:
├── Public
├── Internal
│   ├── General
│   └── IT Department
├── Confidential
│   ├── Finance
│   ├── HR - Employee Data
│   └── Legal - Attorney Client
└── Highly Confidential
    ├── Strategic Planning
    ├── Mergers & Acquisitions
    └── Personal Data
```

**Protection Actions**:
- Encryption settings with user permissions
- Content marking (headers, footers, watermarks)
- Access restrictions and expiration dates
- Rights management integration

### Microsoft Purview Data Loss Prevention (DLP)
**Current DLP Capabilities**:
- DLP policies for Fabric and Power BI now support structured data across multiple item types, not just Power BI semantic models. Supported item types: semantic models, lakehouses, warehouses, KQL databases, mirrored databases, SQL databases, and Cosmos databases
- Detection of sensitive data uploaded into OneLake and into supported Fabric items
- Recognition of sensitivity labels and sensitive information types (credit cards, SSNs)
- Policy tips for Fabric item and semantic model owners, and alerts for security administrators
- **Restrict access** action (in preview) that limits an item to its data owners or to members of the organization when a policy match occurs
- Override capabilities for workspace admins where the policy allows it
- Note: DLP for Fabric evaluates data in Delta-format tables only, requires Fabric or Premium capacity, and doesn't support advanced classifiers (EDM, trainable, credential, and named-entity classifiers)

**DLP Policy Configuration**:
```
DLP Policy Components:
├── Locations (Fabric and Power BI workspaces)
│   └── Item types: semantic models, lakehouses, warehouses,
│       KQL / SQL / mirrored / Cosmos databases
├── Conditions
│   ├── Sensitivity Labels
│   ├── Sensitive Info Types
│   └── Content Patterns
├── Actions
│   ├── Restrict Access (preview)
│   ├── Generate Alerts
│   ├── Policy Tips
│   └── Allow Override
└── Monitoring & Reporting
```

### Microsoft Purview Audit
**Comprehensive Activity Logging**:
- All Microsoft Fabric user activities logged in Purview audit log
- Integration with existing Microsoft 365 audit infrastructure
- Real-time monitoring capabilities
- Advanced hunting and investigation tools

**Audit Coverage**:
- Data access and modification events
- Administrative actions and configuration changes
- User authentication and authorization events
- Data export and sharing activities
- Policy violations and security incidents

### Microsoft Purview Insider Risk Management (IRM)
- Ready-to-use risk indicators for Fabric (Power BI and lakehouse activities)
- Detections specific to Fabric data exfiltration scenarios (for example, exporting Power BI reports or moving data from lakehouse and warehouse assets) via the data theft policy
- IRM reporting to monitor Fabric-related risky activities and help identify potential insider risks

### Microsoft Purview Governance for Fabric Copilots and Agents
- Risk discovery in Copilot/agent prompts and responses
- Audit coverage for AI interactions
- Retention and eDiscovery applicability to AI-generated content
- Detection of non-compliant or risky AI usage across supported Fabric workloads

## 3. Microsoft Purview Hub in Fabric and the OneLake Catalog

### Integrated Governance Experience
The Microsoft Purview Hub provides:
- Insights about Fabric data inventory, sensitivity labels, and endorsements directly within the Fabric interface
- Gateway functionality between Fabric and the broader Purview ecosystem
- Seamless navigation between Fabric workspaces and the Purview portal

> **2026 update:** The security and governance insights previously surfaced in the Microsoft Purview Hub are now available in the **OneLake catalog**, under its **Govern** tab. The OneLake catalog is the centralized in-Fabric governance experience and is organized into three tabs — **Explore**, **Govern**, and **Secure**. The Govern tab for Fabric admins (generally available as of March 2026) provides tenant-wide insights, recommended actions, and reports.

### Govern Tab / Hub Capabilities
- **Data Estate Overview**: Inventory overview, capacities & domains, and feature usage across the tenant ("Manage your data estate")
- **Protect, Secure & Comply**: Sensitivity-label coverage and DLP policy insights across workspaces, with drill-down by item type, user, domain, or workspace
- **Discover, Trust & Reuse**: Data freshness, curation state (description and endorsement coverage), and content sharing views
- **Recommended Actions**: Guided actions to improve the governance posture of your data, with Copilot-assisted exploration

## 4. Advanced Security and Governance Features

### Data Classification and Discovery
**Automated Classification**:
- Built-in sensitive information types for common data patterns
- Custom classification rules for organization-specific data
- Machine learning-powered classification recommendations
- Integration with Microsoft Information Protection scanner

**Data Discovery Process**:
1. **Scanning**: Automated discovery of data across Fabric workspaces
2. **Classification**: Application of sensitivity labels and classifications
3. **Mapping**: Creation of comprehensive data maps with lineage
4. **Monitoring**: Continuous monitoring for new or changed data

### Sensitivity Label Management
**Label Creation and Configuration**:
- Hierarchical label structure with inheritance
- Granular protection settings per label
- Automated label application based on content analysis
- Integration with Azure Rights Management for encryption

**Label Application Strategies**:
- **Manual Labeling**: User-driven label selection
- **Recommended Labeling**: System recommendations with user approval
- **Automatic Labeling**: Policy-driven automatic application
- **Default Labeling**: Workspace or item-level default labels

### Data Lineage and Impact Analysis
**End-to-End Lineage Tracking**:
- Complete data flow from source systems to end-user reports
- Impact analysis for data changes and policy updates
- Dependency mapping for governance decision-making
- Integration with Fabric's native lineage capabilities

**Lineage Visualization**:
```
Data Lineage Flow:
Source Systems → OneLake → Fabric Workspaces → Semantic Models → Reports
     ↓              ↓           ↓               ↓            ↓
  Purview      Purview     Purview        Purview      Purview
 Scanning    Classification  Governance   DLP Policies  Audit Log
```

## 5. Compliance and Risk Management

### Regulatory Compliance Support
**Built-in Compliance Templates**:
- GDPR (General Data Protection Regulation)
- CCPA (California Consumer Privacy Act)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOX (Sarbanes-Oxley Act)
- Industry-specific regulations (PCI DSS, FISMA, etc.)

**Compliance Assessment**:
- Automated compliance scoring and reporting
- Gap analysis and remediation recommendations
- Continuous monitoring for compliance drift
- Integration with Microsoft Compliance Manager

### Risk Assessment and Management
**Data Risk Identification**:
- Sensitive data exposure analysis
- Access privilege reviews and anomaly detection
- Data sharing and collaboration risks
- Cross-border data transfer compliance

**Risk Mitigation Strategies**:
- Automated policy enforcement
- Just-in-time access provisioning
- Data minimization and retention policies
- Incident response and breach notification

## 6. Implementation Strategy

### Phase 1: Foundation Setup (Weeks 1-4)
**Purview Environment Preparation**:
1. Enable Microsoft Purview for the organization
2. Configure Purview Hub in Fabric workspaces
3. Establish basic sensitivity label taxonomy
4. Set up initial DLP policies for Fabric and Power BI

**Basic Integration Configuration**:
- Connect Fabric tenant to Purview catalog
- Enable automatic metadata discovery
- Configure audit log collection
- Establish governance team and roles

### Phase 2: Classification and Protection (Weeks 5-8)
**Data Discovery and Classification**:
1. Run comprehensive scans across Fabric workspaces
2. Apply sensitivity labels to identified sensitive data
3. Configure automatic labeling policies
4. Establish data stewardship workflows

**Policy Implementation**:
- Deploy comprehensive DLP policies
- Configure sensitivity label protection settings
- Implement access governance policies
- Establish compliance monitoring

### Phase 3: Advanced Governance (Weeks 9-12)
**Enhanced Controls**:
1. Implement advanced classification rules
2. Deploy cross-tenant governance policies
3. Configure advanced threat protection
4. Establish automated compliance reporting

**Integration Optimization**:
- Performance tuning of governance policies
- Advanced lineage and impact analysis
- Custom compliance templates
- Integration with third-party governance tools

## 7. Current Capabilities and Limitations

### Available Integrations (As of the July 2026 review)
✅ **Currently Available**:
- Microsoft Purview Unified Catalog and Data Map integration (same-tenant and cross-tenant)
- Information Protection with sensitivity labels on all Fabric items
- Protection policies for access control based on sensitivity labels
- DLP policies for Fabric and Power BI across semantic models, lakehouses, warehouses, and KQL/SQL/mirrored/Cosmos databases (including a restrict-access action in preview)
- Insider Risk Management indicators for Fabric (Power BI and lakehouse), including data-theft detection
- Purview governance and risk controls for Fabric Copilots and agents
- Comprehensive audit logging
- Purview Hub plus the OneLake catalog Govern tab in the Fabric interface

### Limitations and Future Enhancements
**Current Limitations**:
- DLP for Fabric evaluates data in Delta-format tables only and requires Fabric or Premium capacity
- DLP restrict-access action is still in preview
- DLP doesn't support advanced classifiers (exact data match, trainable, credential, and named-entity classifiers) or policy templates (custom policies only)
- Sensitivity-label inheritance from data sources is currently supported for Power BI semantic models only
- Label/protection inheritance on export is currently supported for Power BI items only; other Fabric export paths issue a warning but don't carry the label
- The OneLake catalog Govern tab doesn't support cross-tenant scenarios, guest users, or Private Link environments
- Cross-service policy consistency and real-time enforcement can still require multiple configuration layers (workspace roles, OneLake security, labels, and DLP evaluate independently)

**Areas of Continued Investment**:
- Broader DLP coverage and general availability of restrict-access enforcement
- Wider label inheritance and export protection across non-Power BI Fabric experiences
- Deeper AI governance for Fabric Copilots and agents
- Improved cross-tenant governance capabilities

## 8. Best Practices and Recommendations

### Governance Strategy
**Organizational Structure**:
```
Data Governance Hierarchy:
├── Chief Data Officer (CDO)
├── Data Governance Council
│   ├── Data Stewards (by domain)
│   ├── Privacy Officers
│   └── Compliance Managers
├── Technical Implementation Team
│   ├── Fabric Administrators
│   ├── Purview Administrators
│   └── Security Architects
└── Business Data Owners
```

### Policy Design Principles
1. **Start Simple**: Begin with basic sensitivity labels and gradually add complexity
2. **Business Alignment**: Ensure governance policies align with business objectives
3. **User Experience**: Balance security with usability to ensure adoption
4. **Continuous Improvement**: Regularly review and refine governance policies
5. **Automation**: Leverage automated classification and policy enforcement where possible

### Monitoring and Maintenance
**Regular Activities**:
- Weekly governance dashboard reviews
- Monthly policy effectiveness assessments
- Quarterly compliance audits and reports
- Annual governance strategy reviews

**Key Performance Indicators (KPIs)**:
- Percentage of data assets with applied sensitivity labels
- Policy violation rates and trends
- Mean time to detect and respond to governance issues
- User compliance training completion rates
- Data steward activity and engagement metrics

## 9. Advanced Integration Scenarios

### Multi-Cloud Governance
**Cross-Platform Data Governance**:
- Govern data across Microsoft Fabric, Azure, AWS, and Google Cloud
- Unified policy enforcement across cloud platforms
- Consistent classification and labeling across environments
- Cross-cloud data lineage and impact analysis

### AI and Machine Learning Governance
**Responsible AI Framework**:
- Governance policies for AI model development and deployment
- Sensitive data protection in ML training datasets
- Model bias detection and mitigation
- AI decision auditing and explainability

### Integration with Third-Party Tools
**Ecosystem Connectivity**:
- API-based integration with existing governance tools
- Custom connector development for specialized systems
- Governance policy synchronization across platforms
- Unified reporting and dashboard capabilities

# This comprehensive approach to Microsoft Purview and Fabric integration provides organizations with enterprise-grade data governance, security, and compliance capabilities while maintaining the performance and usability that make Fabric attractive for data analytics implementations.
