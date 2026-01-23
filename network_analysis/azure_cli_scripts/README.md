# Azure CLI Scripts - Network Diagnostics

Azure CLI and bash scripts for infrastructure-level network validation.

---

## 📁 Available Scripts

Each script has its own folder with detailed README and usage instructions.

| Script | Purpose | Environment | README |
|--------|---------|-------------|--------|
| **Private Link Validation** | VM-based Private Link testing | Azure VM / Cloud Shell | [📖 README](private_link_validation/README.md) |
| **Classic Compute Validation** | VNet injection and NSG validation | Azure CLI / Terminal | [📖 README](classic_compute_validation/README.md) |

---

## 🚀 Quick Start

### **Private Link Validation** (Compare VM vs Databricks)
```bash
# Run on Azure VM in same VNet as Databricks
curl -o test.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/private_link_validation/script.sh
chmod +x test.sh

# Edit configuration
nano test.sh

# Run
./test.sh
```
[📖 Full Documentation](private_link_validation/README.md)

---

### **Classic Compute Validation** (VNet/NSG Check)
```bash
# Run from terminal with Azure CLI
curl -o check.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/classic_compute_validation/script.sh
chmod +x check.sh

# Run with parameters
./check.sh --resource-group "my-rg" --vnet-name "my-vnet" --public-subnet "public" --private-subnet "private"
```
[📖 Full Documentation](classic_compute_validation/README.md)

---

## 📊 When to Use Each Script

| Problem | Use This Script |
|---------|----------------|
| Compare VM vs Databricks connectivity | [Private Link Validation](private_link_validation/) |
| Cluster launch failures | [Classic Compute Validation](classic_compute_validation/) |
| Validate VNet configuration | [Classic Compute Validation](classic_compute_validation/) |
| Check NSG rules | [Classic Compute Validation](classic_compute_validation/) |
| Verify subnet delegation | [Classic Compute Validation](classic_compute_validation/) |
| Baseline infrastructure testing | [Private Link Validation](private_link_validation/) |

---

## 💡 Best Practices

1. **Run before Databricks tests** - Validate infrastructure first
2. **Use Private Link Validation for comparison** - Isolate Databricks-specific issues
3. **Run Classic Compute Validation during setup** - Catch configuration errors early
4. **Save script output** - Keep for compliance and documentation
5. **Read individual READMEs** - Each script has detailed troubleshooting guide

---

## 🔍 Comparison: Databricks vs Azure CLI Scripts

| Aspect | Databricks Notebooks | Azure CLI Scripts |
|--------|---------------------|-------------------|
| **Run From** | Databricks notebook | Terminal / VM |
| **Tests** | Databricks perspective | Infrastructure perspective |
| **Use Case** | Application-level | Infrastructure-level |
| **Best For** | Runtime issues | Setup/config validation |

---

## 🆘 Common Workflow

### **Troubleshooting Private Link Issues**

1. **Run Classic Compute Validation** (if using VNet injection)
   - Validates infrastructure setup
   - Checks NSG rules
   
2. **Run Private Link Validation on Azure VM**
   - Tests from infrastructure perspective
   - Establishes baseline
   
3. **Run Databricks Private Link Diagnostics**
   - Tests from Databricks perspective
   - Compare with VM results

### **Setting Up New Workspace**

1. **Run Classic Compute Validation**
   - Before creating workspace
   - Validates VNet/NSG configuration
   
2. **Fix any issues found**
   - Correct NSG rules
   - Fix subnet delegation
   
3. **Create workspace**
   - With validated configuration

---

## 🔗 Links

- **Main Repository**: https://github.com/prabakar2610/Databricks
- **Network Analysis Home**: [../](../)
- **Databricks Notebooks**: [../databricks_notebooks/](../databricks_notebooks/)

---

**Version:** 4.0  
**Last Updated:** 2026-01-24  
**Organization:** Individual folders with dedicated READMEs
