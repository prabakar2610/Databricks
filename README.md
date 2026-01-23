# Azure Databricks Repository

This repository contains tools and utilities for Azure Databricks, organized into two main categories: Docker configurations and Network diagnostics.

---

## 📁 Repository Structure

```
Databricks/
├── docker/              # Docker configurations for Databricks environments
└── network_analysis/    # Network diagnostic tools for Azure Databricks
```

---

## 🐳 docker/

**Docker configurations and custom images for Azure Databricks**

This folder contains various Docker configurations for creating custom Databricks cluster images with pre-installed packages and configurations.

### Contents:

| Folder | Description | Base Image |
|--------|-------------|------------|
| `R/` | R-based environments | R runtime |
| `alphine/` | Alpine Linux minimal images | Alpine |
| `min20/` | Minimal Ubuntu 20.04 setup | Ubuntu 20.04 |
| `python env/` | Python environment configurations | Python |
| `rbase/` | R base configurations | R |
| `rbase-std/` | R standard configurations | R |
| `std20/` | Standard Ubuntu 20.04 images | Ubuntu 20.04 |

### Use Cases:
- Custom cluster images with pre-installed libraries
- Specialized runtime environments (R, Python, etc.)
- Minimal images for optimized performance
- Standard enterprise configurations

### Getting Started:
```bash
cd docker/<your-folder>
docker build -t your-image-name .
```

**📖 Documentation:** See individual folders for specific Dockerfiles and instructions.

---

## 🌐 network_analysis/

**Comprehensive network diagnostic suite for Azure Databricks**

Modular scripts for troubleshooting Azure Databricks networking issues including Private Link, VNet injection, DNS, NSGs, and serverless connectivity.

### Quick Links:
- **Main Guide:** [network_analysis/README.md](./network_analysis/README.md)
- **Databricks Scripts:** [network_analysis/databricks_notebooks/](./network_analysis/databricks_notebooks/)
- **Azure CLI Scripts:** [network_analysis/azure_cli_scripts/](./network_analysis/azure_cli_scripts/)

### Available Scripts:

#### **For Databricks Notebooks** (Python):
1. **Private Link Diagnostics** (`01_private_link_diagnostics.py`)
   - Comprehensive Private Link connectivity testing
   - DNS resolution validation (private vs public)
   - TCP connectivity and reliability testing
   - ⏱️ ~2 minutes

2. **DNS Diagnostics** (`02_dns_diagnostics.py`)
   - Workspace, control plane, and storage DNS
   - Private endpoint detection
   - ⏱️ ~30 seconds

3. **Serverless Diagnostics** (`03_serverless_diagnostics.py`)
   - Serverless compute networking
   - Storage connectivity and egress validation
   - ⏱️ ~1 minute

#### **For Azure CLI** (Bash):
1. **Private Link Validation** (`01_private_link_validation.sh`)
   - Azure VM-based connectivity validation
   - Multi-tool DNS testing
   - Infrastructure comparison

2. **VNet/NSG Validation** (`02_classic_compute_vnet_nsg.sh`)
   - VNet injection configuration
   - NSG rules validation
   - Subnet delegation checks

### Quick Start:

**Test from Databricks Notebook:**
```python
# Example: DNS diagnostics
import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/02_dns_diagnostics.py").text)
```

**Test from Azure CLI:**
```bash
# Download and run VNet validation
curl -o vnet_check.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/02_classic_compute_vnet_nsg.sh
chmod +x vnet_check.sh && ./vnet_check.sh
```

### Common Use Cases:
- ❌ **Can't connect to internal API** → Use Private Link diagnostics
- ❌ **DNS not resolving** → Use DNS diagnostics
- ❌ **Serverless storage issues** → Use Serverless diagnostics
- ❌ **VNet injection problems** → Use VNet/NSG validation
- ❌ **Need infrastructure comparison** → Use both Databricks + Azure CLI scripts

---

## 🚀 Quick Navigation

### **I need to...**

| Task | Go To |
|------|-------|
| Create custom Databricks cluster image | [`docker/`](./docker/) |
| Add pre-installed packages to clusters | [`docker/`](./docker/) |
| Test Private Link connectivity | [`network_analysis/databricks_notebooks/01_private_link_diagnostics.py`](./network_analysis/databricks_notebooks/01_private_link_diagnostics.py) |
| Validate DNS configuration | [`network_analysis/databricks_notebooks/02_dns_diagnostics.py`](./network_analysis/databricks_notebooks/02_dns_diagnostics.py) |
| Troubleshoot serverless networking | [`network_analysis/databricks_notebooks/03_serverless_diagnostics.py`](./network_analysis/databricks_notebooks/03_serverless_diagnostics.py) |
| Check VNet/NSG configuration | [`network_analysis/azure_cli_scripts/02_classic_compute_vnet_nsg.sh`](./network_analysis/azure_cli_scripts/02_classic_compute_vnet_nsg.sh) |
| Compare Azure VM vs Databricks connectivity | Use both folders in [`network_analysis/`](./network_analysis/) |

---

## 📚 Documentation

### Docker:
- See individual folders for Dockerfile configurations
- Base images and package lists documented in each folder

### Network Analysis:
- **Complete Guide:** [network_analysis/README.md](./network_analysis/README.md)
- **Databricks Scripts Guide:** [network_analysis/databricks_notebooks/README.md](./network_analysis/databricks_notebooks/README.md)
- **Azure CLI Scripts Guide:** [network_analysis/azure_cli_scripts/README.md](./network_analysis/azure_cli_scripts/README.md)
- **Troubleshooting Flowchart:** [network_analysis/docs/TROUBLESHOOTING_FLOWCHART.md](./network_analysis/docs/TROUBLESHOOTING_FLOWCHART.md)
- **Quick Reference:** [network_analysis/docs/CHEAT_SHEET.txt](./network_analysis/docs/CHEAT_SHEET.txt)

---

## 🎯 Common Workflows

### **Workflow 1: Set up Custom Databricks Environment**
1. Browse `docker/` for appropriate base configuration
2. Customize Dockerfile with your requirements
3. Build and push to your container registry
4. Configure Databricks cluster to use custom image

### **Workflow 2: Troubleshoot Private Link Issues**
1. Run DNS diagnostics (`network_analysis/databricks_notebooks/02_dns_diagnostics.py`)
2. If DNS shows public IP, run Private Link diagnostics (`01_private_link_diagnostics.py`)
3. Compare with Azure VM validation (`azure_cli_scripts/01_private_link_validation.sh`)
4. Follow troubleshooting guide for specific issues

### **Workflow 3: Validate VNet Injection Setup**
1. Run VNet/NSG validation script (`azure_cli_scripts/02_classic_compute_vnet_nsg.sh`)
2. Fix any NSG or delegation issues found
3. Verify from Databricks with DNS diagnostics
4. Test connectivity with Private Link diagnostics

---

## 🤝 Contributing

Feel free to contribute:
- Add new Docker configurations
- Improve network diagnostic scripts
- Add new diagnostic scenarios
- Enhance documentation

---

## 📞 Support & Resources

### **Official Documentation:**
- [Azure Databricks Documentation](https://docs.microsoft.com/azure/databricks/)
- [Azure Databricks Networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/)
- [Custom Container Images](https://docs.microsoft.com/azure/databricks/clusters/custom-containers)

### **Network Diagnostics:**
- For detailed troubleshooting, see [network_analysis/docs/TROUBLESHOOTING_FLOWCHART.md](./network_analysis/docs/TROUBLESHOOTING_FLOWCHART.md)
- For quick reference, see [network_analysis/docs/CHEAT_SHEET.txt](./network_analysis/docs/CHEAT_SHEET.txt)

---

## 📊 Repository Statistics

| Category | Components | Status |
|----------|------------|--------|
| Docker Configurations | 7 environments | ✅ Active |
| Network Diagnostic Scripts | 5 scripts | ✅ Active |
| Documentation Files | 10+ guides | ✅ Complete |

---

## 🏷️ Tags

`azure-databricks` `docker` `networking` `diagnostics` `private-link` `vnet-injection` `troubleshooting` `azure` `python` `bash`

---

## 📝 Version History

- **v3.0** (2026-01-24): Reorganized into `docker/` and `network_analysis/` folders
- **v2.0** (2026-01-23): Added modular network diagnostics
- **v1.0**: Initial Docker configurations

---

## 📄 License

This repository is maintained for Azure Databricks troubleshooting and configuration purposes.

---

**Repository:** https://github.com/prabakar2610/Databricks

**Quick Links:**
- 🐳 [Docker Configurations](./docker/)
- 🌐 [Network Analysis](./network_analysis/)
