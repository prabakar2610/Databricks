# Azure Databricks Network Diagnostics Suite

Comprehensive, modular network diagnostic tools for Azure Databricks.  
**Each script has its own folder with detailed README and usage instructions.**

---

## 📁 Folder Structure

```
network_analysis/
├── databricks_notebooks/              # Scripts for Databricks Notebooks (%python or %sh)
│   ├── private_link_diagnostics/      ⭐ Comprehensive Private Link testing
│   │   ├── script.py
│   │   └── README.md                  📖 Complete usage guide
│   ├── dns_diagnostics/               DNS configuration validation
│   │   ├── script.py
│   │   └── README.md                  📖 Complete usage guide
│   ├── serverless_diagnostics/        Serverless compute networking
│   │   ├── script.py
│   │   └── README.md                  📖 Complete usage guide
│   ├── mtls_cluster_diagnostics/      Cluster mTLS / TLS config + live checks (Bash)
│   │   ├── script.sh
│   │   └── README.md                  📖 Complete usage guide
│   └── README.md                      Overview of all Databricks scripts
│
├── azure_cli_scripts/                 # Bash scripts for Azure CLI
│   ├── private_link_validation/       Azure VM validation script
│   │   ├── script.sh
│   │   └── README.md                  📖 Complete usage guide
│   ├── classic_compute_validation/    VNet injection & NSG validation
│   │   ├── script.sh
│   │   └── README.md                  📖 Complete usage guide
│   └── README.md                      Overview of all Azure CLI scripts
│
├── docs/                              # Legacy documentation
│   └── ... (archived guides)
│
└── README.md                          # This file
```

---

## 🎯 Quick Navigation

### **By Problem Type**

| Your Problem | Go To Folder | README |
|--------------|--------------|--------|
| Cannot connect to internal API/database | [databricks_notebooks/private_link_diagnostics/](databricks_notebooks/private_link_diagnostics/) | [📖](databricks_notebooks/private_link_diagnostics/README.md) |
| DNS not resolving correctly | [databricks_notebooks/dns_diagnostics/](databricks_notebooks/dns_diagnostics/) | [📖](databricks_notebooks/dns_diagnostics/README.md) |
| Serverless can't reach storage | [databricks_notebooks/serverless_diagnostics/](databricks_notebooks/serverless_diagnostics/) | [📖](databricks_notebooks/serverless_diagnostics/README.md) |
| Cluster launch failures | [azure_cli_scripts/classic_compute_validation/](azure_cli_scripts/classic_compute_validation/) | [📖](azure_cli_scripts/classic_compute_validation/README.md) |
| Compare VM vs Databricks connectivity | [azure_cli_scripts/private_link_validation/](azure_cli_scripts/private_link_validation/) | [📖](azure_cli_scripts/private_link_validation/README.md) |
| mTLS / TLS differs between clusters | [databricks_notebooks/mtls_cluster_diagnostics/](databricks_notebooks/mtls_cluster_diagnostics/) | [📖](databricks_notebooks/mtls_cluster_diagnostics/README.md) |

### **By Environment**

**Running in Databricks Notebook?**  
→ [databricks_notebooks/](databricks_notebooks/)

**Running from Terminal/VM?**  
→ [azure_cli_scripts/](azure_cli_scripts/)

---

## 🚀 Quick Start Examples

### **Example 1: Test Private Link from Databricks**

```python
# In Databricks notebook
DOMAINS_TO_TEST = [{"host": "api.yourdomain.com", "port": 443, "description": "API"}]
PRIVATE_DNS_ZONE = "yourdomain.com"
NCC_DOMAIN = "yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/private_link_diagnostics/script.py").text)
```

📖 [Full Guide](databricks_notebooks/private_link_diagnostics/README.md)

---

### **Example 2: Quick DNS Check**

```python
# In Databricks notebook - no configuration needed
import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/dns_diagnostics/script.py").text)
```

📖 [Full Guide](databricks_notebooks/dns_diagnostics/README.md)

---

### **Example 3: Validate VNet Configuration**

```bash
# From terminal with Azure CLI
curl -o check.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/classic_compute_validation/script.sh
chmod +x check.sh
./check.sh --resource-group "my-rg" --vnet-name "my-vnet" --public-subnet "public" --private-subnet "private"
```

📖 [Full Guide](azure_cli_scripts/classic_compute_validation/README.md)

---

### **Example 4: Cluster mTLS / TLS diagnostics (`%sh`)**

```bash
# In Databricks notebook — download then run on cluster
curl -fsSL -o /tmp/mtls_cluster_diag.sh \
  https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/mtls_cluster_diagnostics/script.sh
bash /tmp/mtls_cluster_diag.sh mtls-endpoint.example.com 443 /etc/ssl/client.crt /etc/ssl/client.key /etc/ssl/ca.crt
```

📖 [Full Guide](databricks_notebooks/mtls_cluster_diagnostics/README.md)

---

## 📊 Script Comparison Matrix

| Script | Run From | Time | Best For | README |
|--------|----------|------|----------|--------|
| **Private Link Diagnostics** | Databricks | 2 min | Internal resource connectivity | [📖](databricks_notebooks/private_link_diagnostics/README.md) |
| **DNS Diagnostics** | Databricks | 30 sec | DNS resolution issues | [📖](databricks_notebooks/dns_diagnostics/README.md) |
| **Serverless Diagnostics** | Databricks | 1 min | Serverless networking | [📖](databricks_notebooks/serverless_diagnostics/README.md) |
| **Private Link Validation** | Azure VM | 2 min | Infrastructure comparison | [📖](azure_cli_scripts/private_link_validation/README.md) |
| **Classic Compute Validation** | Azure CLI | 1 min | VNet injection validation | [📖](azure_cli_scripts/classic_compute_validation/README.md) |
| **Cluster mTLS Diagnostics** | Databricks `%sh` | 2–5 min | mTLS/TLS parity across clusters | [📖](databricks_notebooks/mtls_cluster_diagnostics/README.md) |

---

## 💡 How to Use This Repository

### **Step 1: Identify Your Problem**

Use the "By Problem Type" table above to find the right script.

### **Step 2: Navigate to Script Folder**

Each script has its own folder with:
- ✅ **script.py** or **script.sh** - The actual script
- ✅ **README.md** - Comprehensive usage guide, troubleshooting, examples

### **Step 3: Read the README**

Each README contains:
- 📋 Overview and when to use
- 🚀 Multiple usage methods (copy-paste, GitHub URL, download)
- ⚙️ Configuration parameters
- 📊 What it tests
- 📤 Sample output
- 🆘 Troubleshooting common issues
- 💡 Tips and best practices
- 📖 Related documentation

### **Step 4: Run the Script**

Follow the usage instructions in the specific README.

---

## 🆘 Common Troubleshooting Workflows

### **Workflow 1: Private Link Not Working**

1. **DNS Diagnostics** ([📖](databricks_notebooks/dns_diagnostics/README.md))
   - Check if DNS resolves to private IP
   
2. **Private Link Validation on VM** ([📖](azure_cli_scripts/private_link_validation/README.md))
   - Verify infrastructure works from VM
   
3. **Private Link Diagnostics in Databricks** ([📖](databricks_notebooks/private_link_diagnostics/README.md))
   - Detailed Databricks-side testing
   
4. **Compare Results**
   - If VM passes but Databricks fails → Databricks config issue
   - If both fail → Infrastructure issue

---

### **Workflow 2: New Workspace Setup**

1. **Classic Compute Validation** ([📖](azure_cli_scripts/classic_compute_validation/README.md))
   - Validate VNet/NSG before workspace creation
   
2. **Fix Issues** (if any)
   - Correct NSG rules
   - Fix subnet delegation
   
3. **Create Workspace**
   
4. **DNS Diagnostics** ([📖](databricks_notebooks/dns_diagnostics/README.md))
   - Verify workspace connectivity

---

### **Workflow 3: Serverless Issues**

1. **Serverless Diagnostics** ([📖](databricks_notebooks/serverless_diagnostics/README.md))
   - Check serverless compute networking
   
2. **DNS Diagnostics** ([📖](databricks_notebooks/dns_diagnostics/README.md))
   - If storage access fails, check DNS

---

### **Workflow 4: mTLS / TLS Works on One Cluster Only**

1. **Cluster mTLS Diagnostics** ([📖](databricks_notebooks/mtls_cluster_diagnostics/README.md))
   - Run on both clusters with the same target host and cert paths; save `/tmp/mtls_diag_<hostname>.txt` to DBFS
2. **Diff outputs** locally or in a notebook to spot Java/OpenSSL, proxy, Spark SSL, truststore, or handshake differences
3. **DNS / Private Link** — if TCP fails on one side only, use [DNS Diagnostics](databricks_notebooks/dns_diagnostics/README.md) and [Private Link Diagnostics](databricks_notebooks/private_link_diagnostics/README.md)

---

## 🎨 Design Philosophy

### **Why Individual Folders?**

✅ **Organized** - Easy to find what you need  
✅ **Comprehensive** - Each README is a complete guide  
✅ **Self-contained** - Everything in one place  
✅ **Maintainable** - Update one script without affecting others  
✅ **Discoverable** - Clear structure for new users

### **Benefits**

1. ✅ No massive monolithic scripts
2. ✅ Detailed troubleshooting per script
3. ✅ Faster execution (smaller, focused scripts)
4. ✅ Use only what you need
5. ✅ Easy to share individual scripts

---

## 📖 Additional Resources

### **Overview READMEs**

- **All Databricks Scripts**: [databricks_notebooks/README.md](databricks_notebooks/README.md)
- **All Azure CLI Scripts**: [azure_cli_scripts/README.md](azure_cli_scripts/README.md)

### **Individual Script READMEs**

Each script folder contains a complete README with:
- Detailed usage instructions
- Configuration examples
- Troubleshooting guides
- Sample outputs
- Related documentation links

### **Microsoft Documentation**

- [Azure Databricks Networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/)
- [Private Link for Databricks](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/pl-to-internal-network)
- [Serverless Networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/)
- [VNet Injection](https://learn.microsoft.com/en-us/azure/databricks/security/network/classic/vnet-inject)

---

## 🔗 Links

- **GitHub Repository**: https://github.com/prabakar2610/Databricks
- **Repository Root**: [../](../)
- **Docker Tools**: [../docker/](../docker/)

---

## ✨ What's New

### v4.1 (2026-03-28)

- ✅ **Cluster mTLS Diagnostics** — [`databricks_notebooks/mtls_cluster_diagnostics/`](databricks_notebooks/mtls_cluster_diagnostics/) Bash script for config collection and active TLS/mTLS checks; compare outputs across clusters

### v4.0

**Major Reorganization:**
- ✅ Each script in its own folder
- ✅ Comprehensive README per script
- ✅ Better organization and discoverability
- ✅ Self-contained documentation
- ✅ Easier to navigate and use

**Previous versions:**
- v3.0: Modular scripts split by topic
- v2.0: Enhanced diagnostics
- v1.0: Initial comprehensive script

---

**Version:** 4.1  
**Last Updated:** 2026-03-28  
**Organization:** Individual folders with comprehensive READMEs  
**Maintained by:** Network Diagnostics Team
