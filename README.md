# msft-fabric

A curated knowledge base for practitioners working with **Microsoft Fabric**. This repository collects battle-tested guides, cheatsheets, and reference implementations covering governance, security, naming standards, and day-to-day engineering across the Fabric platform. Use it as a quick reference when building, securing, and administering Fabric workloads.

## Contents

### Guides & Best Practices

| File | Description |
| --- | --- |
| [fabric_naming_guide.md](fabric_naming_guide.md) | Naming standards and conventions for Fabric workspaces and items (medallion layers, workloads, artifacts). |
| [fabric_pbi_tenant_admin_best_practices.md](fabric_pbi_tenant_admin_best_practices.md) | Recommended Fabric / Power BI tenant admin settings and governance best practices. |
| [fabric_purview_guide.md](fabric_purview_guide.md) | Microsoft Purview + Fabric security and governance integration guide. |
| [Microsoft Purview Integration with Microsoft Fabric.docx](Microsoft%20Purview%20Integration%20with%20Microsoft%20Fabric.docx) | Word-document companion to the Purview markdown guide above. |
| [fabric_security_guide.md](fabric_security_guide.md) | Fabric data-analytics security framework (OneLake, RLS/CLS, Power BI, workspace security). |

### Cheatsheets

| File | Description |
| --- | --- |
| [fabric_pyspark_cheatsheet.md](fabric_pyspark_cheatsheet.md) | PySpark / `notebookutils` cheatsheet for Fabric notebooks. |
| [fabric_warehouse_sql_cheatsheet.md](fabric_warehouse_sql_cheatsheet.md) | T-SQL cheatsheet for the Fabric Data Warehouse. |
| [git_azure_devops_cheatsheet.md](git_azure_devops_cheatsheet.md) | Git + Azure DevOps command cheatsheet. |

### Code & Notebooks

| File | Description |
| --- | --- |
| [scd2-fabric-notebook.py](scd2-fabric-notebook.py) | SCD Type 2 upsert implementation for large Delta tables in Fabric (cell-delimited notebook). |

## How to use

This material is aimed at **data engineers**, **analytics engineers**, and **Fabric / Power BI administrators**.

- Browse the **Guides & Best Practices** when standing up a new workspace, hardening security, or defining governance and naming conventions.
- Keep the **Cheatsheets** handy for quick syntax lookups while working in notebooks, the warehouse, or source control.
- Adapt the **Code & Notebooks** as starting points for your own pipelines — review and test against your own environment before using them in production.

## Disclaimer

Microsoft Fabric evolves rapidly, and features, defaults, and recommended settings change frequently. Always confirm details against the current [Microsoft Learn documentation](https://learn.microsoft.com/fabric/) before acting on anything here. This material was last reviewed **July 2026**.
