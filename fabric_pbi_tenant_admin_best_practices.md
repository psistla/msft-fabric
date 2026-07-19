# Microsoft Fabric / Power BI Tenant Admin Settings - Best Practices Guide

## Overview

Tenant settings enable fine-grained control over the features that are made available to your organization. These settings help establish governance policies and control feature availability across your Microsoft Fabric and Power BI environment.

Because Power BI is now part of Microsoft Fabric, these settings are configured in the **Fabric Admin portal** (open the settings/gear icon in the Fabric portal, then select **Admin portal** under **Governance and insights**, then **Tenant settings**). Microsoft's documentation now frames these collectively as **Fabric tenant settings**, and many of them span the entire Fabric platform rather than just Power BI. For the complete, current list, see the official [Tenant settings index](https://learn.microsoft.com/fabric/admin/tenant-settings-index).

> Note: Tenant settings are governance tools, not security measures. For example, disabling an export setting doesn't remove a user's underlying permission to query a semantic model. Combine these settings with proper data modeling, row-level security, sensitivity labels, and Conditional Access.

Here's a guide to some of the most important tenant settings and their recommended configurations. Setting names change over time; always confirm the current name and behavior in the Fabric Admin portal and the linked Microsoft Learn documentation.

## Key Categories of Tenant Settings

### 1. **Export and Sharing Settings**

#### Export Data Settings
- **Export to Excel**: **Recommended: Enabled for entire organization (or most users)**
  - Microsoft's general guidance is to keep export broadly available so as not to limit productivity, and to monitor usage via the activity log rather than blocking it
  - Fabric automatically applies the item's sensitivity label to the exported file and honors any encryption the label enforces
  - Restrict only where a specific regulatory requirement applies

- **Export to .csv**: **Recommended: Enabled for entire organization (or most users)**
  - Note: .csv is an export path that does **not** carry sensitivity-label protection, so consider restricting it in highly regulated scenarios
  - Apply the same monitoring approach as Excel export

- **Export reports as PowerPoint presentations or PDF documents**: **Recommended: Enabled for entire organization**
  - PowerPoint and PDF are now controlled by a single combined setting
  - These are supported protection paths (the sensitivity label and its encryption follow the exported file)
  - Useful for executive reporting and formatted sharing

- **Paginated report export formats (MHTML, Word, XML, image files)**: **Recommended: Enabled per business need**
  - These are separate settings; MHTML, XML, and image (PNG) outputs do **not** carry sensitivity-label protection
  - Disable specific formats only when regulatory requirements demand it

#### External Sharing Settings
- **Users can invite guest users to collaborate through item sharing and permissions**: **Recommended: Disabled or Enabled for specific groups**
  - This setting was previously called **Share content with external users**
  - Inviting a guest also requires the Microsoft Entra **Guest Inviter** role; this setting only controls invitation through Fabric sharing/permissions experiences
  - High exposure risk if enabled organization-wide; enable only for business units that require external collaboration

- **Guest users can access Microsoft Fabric**: **Recommended: Enabled for specific groups**
  - This setting was previously named **Allow Azure Active Directory guest users to access Power BI**; guest users are managed as Microsoft Entra B2B guests
  - Controls whether Microsoft Entra B2B guest users can access Fabric and the items they have permissions to
  - Related guest settings to review: **Guest users can browse and access Fabric content** and **Users can see guest users in lists of suggested people**
  - Microsoft Entra external collaboration settings and Conditional Access policies are prerequisites and apply on top of these settings

- **Publish to web**: **Recommended: Disabled or restricted to specific groups**
  - Publicly published reports require no authentication to view, so this is one of the highest data-exposure settings
  - If enabled, prefer **Allow only existing embed codes** and review existing embed codes regularly

- **External data sharing (OneLake)**: **Recommended: Disabled or Enabled for specific approved users**
  - Lets specified users share read-only links to OneLake data with collaborators inside and outside the organization
  - Review the associated security considerations before enabling; also review the companion setting **Users can accept external data shares**
  - This is distinct from **Allow specific users to turn on external data sharing**, which governs in-place sharing of Power BI semantic models via Entra B2B

### 2. **Developer and Integration Settings**

#### API Access (Developer settings)
- **Service principals can call Fabric public APIs**: **Recommended: Enabled for specific groups**
  - This is the current name for what used to be "Allow service principals to use Power BI APIs"
  - Essential for automation and integration; restrict to IT/DevOps teams via dedicated security groups
  - A service principal has access to any tenant setting it's enabled for, so scope carefully

- **Service principals can create workspaces, connections, and deployment pipelines**: **Recommended: Enabled for specific groups**
  - Disabled by default for new customers; enable only for approved automation service principals

- **Allow service principals to create and use profiles**: **Recommended: Enabled for specific groups**
  - Required for multitenancy embedding scenarios; limit to trusted service principals only

- **Service principals can access read-only admin APIs** / **Service principals can access admin APIs used for updates** (Admin API settings): **Recommended: Enabled for specific groups**
  - These are separate settings from the developer API settings above; the read-only setting is what Microsoft Purview and metadata-scanning solutions rely on
  - Grant only to service principals in a dedicated, tightly governed security group

- **Embed content in apps**: **Recommended: Enabled for specific groups**
  - Required for the "embed for your customers" scenario; restrict to development teams

#### Custom / Organizational Visuals (Power BI visuals settings)
- **Add and use certified Power BI visuals only**: **Recommended: Enabled**
  - Restricts users to Microsoft-certified visuals, reducing the risk of unreviewed code
  - Balance security against genuine business needs for uncertified visuals

- **Allow visuals created using the Power BI SDK**: **Recommended: Disabled or Enabled for specific groups**
  - This replaces the older "Add and use custom visuals" setting and governs uploading .pbiviz files and adding AppSource visuals
  - Disabled by default; enable via an approval process and review approved visuals regularly
  - Consider the related settings **Allow downloads from custom visuals** and **Allow access to the browser's local storage**
  - Note: the Fabric Admin portal toggles affect the Power BI service; to enforce equivalent behavior in Power BI Desktop, use group policies

### 3. **Workspace and Content Management**

#### Workspace Creation
- **Create workspaces**: **Recommended: Enabled for specific groups**
  - Prevent workspace sprawl by limiting creation rights
  - Typically enable for content creators and team leads
  - Implement naming conventions and governance policies

#### App Settings
- **Create template organizational apps**: **Recommended: Enabled for specific groups**
  - Restrict to approved developers/publishers and implement a review process
  - Monitor distribution and usage

- **Publish apps to the entire organization**: **Recommended: Enabled for specific groups**
  - Controls who can publish an app to everyone rather than to specific groups
  - Limit to approved content creators to maintain quality and governance
  - Note: legacy "content packs" have been retired; app distribution is now governed by settings such as this and **Push apps to end users**

#### Git Integration and Lifecycle (newer settings worth reviewing)
- **Users can synchronize workspace items with their Git repositories** (Azure DevOps) and **...with GitHub repositories**: **Recommended: Enabled for specific groups**
  - Enabled by default; supports source control and CI/CD but connects workspaces to external repositories
  - Control of these switches can be delegated to capacity and workspace admins
  - Also review **Users can export items to Git repositories in other geographical locations** if data residency matters
  - Git integration for non-Power BI Fabric items also requires **Users can create Fabric items** to be on

### 4. **Integration and Networking Settings**

#### Integration settings
- **Use global search for Power BI**: **Recommended: Enabled for entire organization**
  - Improves content discoverability with minimal security implications

- **Allow XMLA endpoints and Analyze in Excel with on-premises semantic models**: **Recommended: Enabled for specific groups**
  - Enables Excel live connections and tool access to the XMLA endpoint; scope where sensitive data is involved

- **Semantic Model Execute Queries REST API**: **Recommended: Enabled for specific groups**
  - Governs querying semantic models via DAX through the REST API

> Note: The on-premises data gateway is managed on the dedicated gateway management pages of the Admin portal (and via Microsoft Entra security groups for gateway admins) rather than as a simple tenant-setting toggle. Restrict gateway administration to a small, trusted group and monitor it closely.

#### Networking settings (newer, for regulated environments)
- **Tenant-level Private Link** and **Block Public Internet Access**: **Recommended: Evaluate for high-security tenants**
  - Allow private-endpoint access to your Fabric tenant and optionally block public-internet access
  - Enabling public-access blocking can take 10-20 minutes to take effect
  - Workspace-level inbound/outbound network rules can also be delegated to workspace admins

### 5. **Security, Compliance, and Information Protection**

#### Audit and usage
- **Usage metrics for content creators**: **Recommended: Enabled for entire organization (or most creators)**
  - Lets creators see usage metrics for content they have permission to; consider **Per-user data in usage metrics for content creators** separately to control exposure of names/emails

#### Information Protection
- **Allow users to apply sensitivity labels for Power BI content**: **Recommended: Enabled for entire organization**
  - Essential for data governance and compliance; integrates with Microsoft Purview Information Protection
  - Consider companion settings for label inheritance from data sources and downstream inheritance for automated labeling

- **Restrict content with protected labels from being shared via link with everyone in your organization**: **Recommended: Enabled**
  - Prevents "People in your organization" sharing links for content whose label carries protection (encryption/markings)
  - Requires both label application and org-wide shareable links to be enabled to take effect; coordinate with your compliance team
  - Do not confuse this with the similarly named **Allow shareable links to grant access to everyone in your organization** (which governs who can create org-wide links regardless of label)

- **Allow workspace admins to override automatically applied sensitivity labels**: **Recommended: Enabled (with activity-log monitoring)**
  - Lets workspace admins fix/override labels that were applied automatically, avoiding lockout scenarios

> Consider Microsoft Purview **protection policies** for Fabric, which enforce access control based on sensitivity labels beyond what tenant settings alone provide.

### 6. **Advanced Analytics and AI Settings**

#### Copilot and Azure OpenAI (newer, high-importance settings)
- **Users can use Copilot and other features powered by Azure OpenAI**: **Recommended: Enabled per governance decision**
  - Governs access to Copilot and Fabric AI features; can be managed at both the tenant and capacity levels
  - Review data-handling and (for EU customers) EU Data Boundary implications, and note that AI features in preview are subject to preview terms
  - Related preview setting: **Users can access a standalone, cross-item Power BI Copilot experience**

#### Insights
- **Show entry points for insights (preview)** and **Receive notifications for top insights (preview)**: **Recommended: Enabled for entire organization**
  - These are the current insights tenant settings (the older "Quick Insights" experience has been retired)
  - Low security risk; help users discover patterns in data

#### Advanced Analytics
- **Use ArcGIS Maps for Power BI**: **Recommended: Enabled for specific groups**
  - Geographic visualization provided by Esri; may have licensing and data-processing implications
  - Related: **Users can use the Azure Maps visual** (note that location data may be processed by Microsoft)

- **Interact with and share R and Python visuals**: **Recommended: Enabled per business need**
  - Applies to the entire organization (can't be scoped to specific groups); evaluate the code-execution surface

## Implementation Best Practices

### 1. **Phased Rollout Approach**
- Start with restrictive settings and gradually open access
- Test changes with pilot groups before organization-wide deployment
- It can take up to 15 minutes for a setting change to take effect for everyone in your organization (as stated in current Microsoft documentation); some networking changes, such as blocking public internet access, can take 10-20 minutes

### 2. **Security Group Strategy**
- Create dedicated security groups for different permission levels
- Use meaningful names that reflect purpose (e.g., "PowerBI-ExportData-Analysts")
- Document group memberships and purposes
- Regular access reviews and cleanup

### 3. **Monitoring and Governance**
- Enable audit logging for all critical settings
- Regular review of tenant settings
- Monitor for new settings additions - Microsoft frequently adds new tenant settings, and the tenant settings page shows a banner listing new and changed settings (each flagged with a "new" icon)
- Consider extracting the current state programmatically with the **Get Tenant Settings** / List Tenant Settings admin REST API for auditing
- Implement change management processes

### 4. **Documentation and Training**
- Document all tenant setting decisions with business justifications
- Train administrators on security implications
- Create user guides for approved features
- Maintain settings inventory and review schedule

## Critical Security Considerations

### High-Risk Settings to Monitor Closely
1. **External sharing capabilities** - Highest data exposure risk
2. **API access permissions** - Potential for automation abuse
3. **Custom visual permissions** - Code execution risks
4. **Export permissions** - Data exfiltration concerns

### Recommended Review Schedule
- **Monthly**: Review new tenant settings and security group memberships
- **Quarterly**: Full audit of all tenant settings and their usage
- **Annually**: Complete governance policy review and updates

## Compliance Considerations

### Data Residency
- Review data storage location settings
- Ensure compliance with regional data protection laws
- Configure appropriate data residency options

### Audit and Reporting
- Enable comprehensive audit logging
- Regular compliance reporting
- Integration with SIEM systems where required

## Emergency Procedures

### Incident Response
- Document procedures for quickly disabling problematic settings
- Maintain emergency contact lists for tenant administrators
- Regular testing of emergency response procedures

### Backup and Recovery
- Document current tenant configuration
- Implement configuration backup processes
- Test recovery procedures

## Conclusion

Microsoft Fabric and Power BI tenant administration requires careful balance between security, governance, and user productivity. The settings outlined above provide a foundation for a secure Fabric and Power BI deployment while enabling business value. Because Microsoft ships new and renamed tenant settings frequently, treat this guide as a starting point and verify current names, defaults, and scoping options against the official [Tenant settings index](https://learn.microsoft.com/fabric/admin/tenant-settings-index). Regular review and adjustment based on organizational needs and the evolving threat landscape is essential.

Remember that tenant settings are governance tools rather than security measures - they should be part of a broader security and governance strategy that includes proper data modeling, row-level security, sensitivity labels and Purview protection policies, Microsoft Entra Conditional Access, and user training.