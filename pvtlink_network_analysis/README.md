# Azure Databricks Network Diagnostics - Modular Suite

Comprehensive, modular network diagnostics for Azure Databricks.  
Split into focused scripts by topic and environment (Databricks vs Azure CLI).

## 📁 Folder Structure

```
pvtlink_network_analysis/
├── databricks_notebooks/           # Scripts for Databricks Notebooks
│   ├── 01_private_link_diagnostics.py   ⭐ Comprehensive Private Link testing
│   ├── 02_dns_diagnostics.py            DNS configuration validation
│   ├── 03_serverless_diagnostics.py     Serverless compute networking
│   └── README.md                        Detailed notebook scripts guide
│
├── azure_cli_scripts/              # Scripts for Azure CLI (infrastructure)
│   ├── 01_private_link_validation.sh    Azure VM validation script
│   ├── 02_classic_compute_vnet_nsg.sh   VNet injection & NSG validation
│   └── README.md                        Detailed CLI scripts guide
│
├── docs/                           # Documentation (legacy)
│   ├── START_HERE.md
│   ├── TROUBLESHOOTING_FLOWCHART.md
│   ├── CHEAT_SHEET.txt
│   └── ... (other guides)
│
└── README.md                       # This file
```

---

## 🎯 Quick Start

### **1. For Databricks Issues**

Use scripts in `databricks_notebooks/` - run directly in Databricks notebooks:

```python
# Example: Test Private Link connectivity
import requests
URL = "https://raw.githubusercontent.com/prabakar2610/Databricks/master/pvtlink_network_analysis/databricks_notebooks/01_private_link_diagnostics.py"
exec(requests.get(URL).text)
```

### **2. For Infrastructure Validation**

Use scripts in `azure_cli_scripts/` - run from terminal with Azure CLI:

```bash
cd azure_cli_scripts
./02_classic_compute_vnet_nsg.sh
```

---

## 📋 Choose the Right Script

### **Problem: Can't connect to internal API/database**
→ Use: `databricks_notebooks/01_private_link_diagnostics.py`

### **Problem: DNS not resolving correctly**
→ Use: `databricks_notebooks/02_dns_diagnostics.py`

### **Problem: Serverless can't reach storage**
→ Use: `databricks_notebooks/03_serverless_diagnostics.py`

### **Problem: Need to validate VNet/NSG configuration**
→ Use: `azure_cli_scripts/02_classic_compute_vnet_nsg.sh`

### **Problem: Compare Azure VM vs Databricks connectivity**
→ Use both:
  - `azure_cli_scripts/01_private_link_validation.sh` (on Azure VM)
  - `databricks_notebooks/01_private_link_diagnostics.py` (in Databricks)

---

## 🎨 Design Philosophy

### **Modular Approach**
- ✅ Small, focused scripts by topic
- ✅ Use only what you need
- ✅ Easy to maintain and extend
- ✅ No massive monolithic scripts

### **Environment Separation**
- **Databricks Notebooks**: Test from Databricks perspective (Python)
- **Azure CLI Scripts**: Test from Azure infrastructure perspective (Bash)

### **Benefits**
1. Faster execution (smaller scripts)
2. Easier troubleshooting (focused scope)
3. Better organization (logical grouping)
4. Simpler configuration (only relevant settings)

---

## 🚀 Usage Examples

### **Example 1: Private Link Not Working**

**Step 1:** Run DNS diagnostics
```python
# In Databricks notebook
import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/pvtlink_network_analysis/databricks_notebooks/02_dns_diagnostics.py").text)
```

**Step 2:** If DNS shows public IP, run detailed Private Link diagnostics
```python
# Configure
DOMAINS_TO_TEST = [{"host": "api.yourdomain.com", "port": 443}]
PRIVATE_DNS_ZONE = "yourdomain.com"
NCC_DOMAIN = "yourdomain.com"

# Run
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/pvtlink_network_analysis/databricks_notebooks/01_private_link_diagnostics.py").text)
```

**Step 3:** Compare with Azure VM
```bash
# On Azure VM in same VNet
./azure_cli_scripts/01_private_link_validation.sh
```

---

### **Example 2: VNet Injection Issues**

**Step 1:** Validate infrastructure
```bash
# Edit configuration
nano azure_cli_scripts/02_classic_compute_vnet_nsg.sh

# Run validation
./azure_cli_scripts/02_classic_compute_vnet_nsg.sh
```

**Step 2:** Test from Databricks
```python
# Run DNS diagnostics to verify
exec(requests.get("...02_dns_diagnostics.py").text)
```

---

### **Example 3: Serverless Storage Issues**

**Step 1:** Run serverless diagnostics
```python
# In Databricks notebook with Serverless compute
exec(requests.get("...03_serverless_diagnostics.py").text)
```

---

## 📊 Script Comparison Matrix

| Script | Scope | Run From | Time | Best For |
|--------|-------|----------|------|----------|
| 01_private_link_diagnostics.py | Private Link | Databricks | 2 min | Internal resource connectivity |
| 02_dns_diagnostics.py | DNS | Databricks | 30 sec | DNS resolution issues |
| 03_serverless_diagnostics.py | Serverless | Databricks | 1 min | Serverless networking |
| 01_private_link_validation.sh | Private Link | Azure VM | 2 min | Infrastructure comparison |
| 02_classic_compute_vnet_nsg.sh | VNet/NSG | Azure CLI | 1 min | VNet injection validation |

---

## 💡 Best Practices

1. **Start Simple**: Begin with DNS diagnostics (02)
2. **Go Deeper**: Use focused scripts for specific issues
3. **Compare Environments**: Run both Databricks and Azure CLI scripts
4. **Save Results**: JSON output from all scripts - save for comparison
5. **Incremental Testing**: Fix one thing at a time, re-test

---

## 🆘 Common Workflows

### **Workflow 1: New Private Link Setup**
1. Run `02_dns_diagnostics.py` → Check DNS resolution
2. Run `01_private_link_diagnostics.py` → Detailed Private Link test
3. If failing, run `01_private_link_validation.sh` from Azure VM
4. Compare results to isolate issue

### **Workflow 2: VNet Injection Setup**
1. Run `02_classic_compute_vnet_nsg.sh` → Validate infrastructure
2. Fix any NSG/delegation issues found
3. Run `02_dns_diagnostics.py` → Verify from Databricks perspective

### **Workflow 3: Serverless Issues**
1. Run `03_serverless_diagnostics.py` → Check serverless connectivity
2. If storage fails, check DNS with `02_dns_diagnostics.py`
3. Validate Azure side with CLI scripts

---

## 📖 Documentation

- **Databricks Scripts**: See `databricks_notebooks/README.md`
- **Azure CLI Scripts**: See `azure_cli_scripts/README.md`
- **Troubleshooting Guide**: See `docs/TROUBLESHOOTING_FLOWCHART.md`
- **Quick Reference**: See `docs/CHEAT_SHEET.txt`

---

## 🔗 Links

- **GitHub**: https://github.com/prabakar2610/Databricks/tree/master/pvtlink_network_analysis
- **Microsoft Docs**: https://learn.microsoft.com/en-us/azure/databricks/security/network/

---

## ✨ What's New (v3.0)

**New Modular Structure:**
- ✅ Split into databricks_notebooks/ and azure_cli_scripts/
- ✅ Focused scripts by topic (Private Link, DNS, Serverless, VNet/NSG)
- ✅ Separate READMEs for each folder
- ✅ Easier to find and use the right script

**Legacy Scripts:**
- Original comprehensive scripts moved to `databricks_notebooks/01_private_link_diagnostics.py`
- All documentation preserved in `docs/` folder

---

## 🎓 Learning Path

**Beginner:**
1. Read this README
2. Read `databricks_notebooks/README.md`
3. Try `02_dns_diagnostics.py` (simplest script)

**Intermediate:**
1. Use `01_private_link_diagnostics.py` for specific issues
2. Learn Azure CLI scripts for infrastructure validation
3. Read troubleshooting flowchart

**Advanced:**
1. Combine multiple scripts for comprehensive analysis
2. Automate with your own wrapper scripts
3. Extend with custom tests

---

## 📝 Migration from v2.0

**Old Way:**
```python
# Single large script
exec(requests.get(".../databricks_private_link_diagnostics_enhanced.py").text)
```

**New Way:**
```python
# Focused scripts
exec(requests.get(".../databricks_notebooks/02_dns_diagnostics.py").text)  # DNS only
exec(requests.get(".../databricks_notebooks/01_private_link_diagnostics.py").text)  # Private Link
```

**Benefits:**
- Faster (smaller scripts)
- Easier to configure (fewer options)
- More maintainable

---

**Version:** 3.0  
**Last Updated:** 2026-01-24  
**Maintained by:** Network Diagnostics Team
