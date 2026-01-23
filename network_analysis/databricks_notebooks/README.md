# Databricks Notebooks - Network Diagnostics

Network diagnostic scripts designed to run in **Azure Databricks Notebooks**.

---

## 📁 Available Scripts

Each script has its own folder with detailed README and usage instructions.

| Script | Purpose | Run Time | README |
|--------|---------|----------|--------|
| **Private Link Diagnostics** | Comprehensive Private Link connectivity testing | ~2 min | [📖 README](private_link_diagnostics/README.md) |
| **DNS Diagnostics** | DNS resolution and configuration validation | ~30 sec | [📖 README](dns_diagnostics/README.md) |
| **Serverless Diagnostics** | Serverless compute networking validation | ~1 min | [📖 README](serverless_diagnostics/README.md) |

---

## 🚀 Quick Start

### **Private Link Issues**
```python
DOMAINS_TO_TEST = [{"host": "api.yourdomain.com", "port": 443, "description": "API"}]
PRIVATE_DNS_ZONE = "yourdomain.com"
NCC_DOMAIN = "yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/private_link_diagnostics/script.py").text)
```
[📖 Full Documentation](private_link_diagnostics/README.md)

---

### **DNS Issues**
```python
# Minimal - auto-detects workspace
import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/dns_diagnostics/script.py").text)
```
[📖 Full Documentation](dns_diagnostics/README.md)

---

### **Serverless Issues**
```python
STORAGE_ACCOUNTS = [{"name": "yourstorageaccount", "test_adls": True, "test_blob": True}]

import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/serverless_diagnostics/script.py").text)
```
[📖 Full Documentation](serverless_diagnostics/README.md)

---

## 📊 When to Use Each Script

| Problem | Use This Script |
|---------|----------------|
| Cannot connect to internal API/database | [Private Link Diagnostics](private_link_diagnostics/) |
| DNS not resolving correctly | [DNS Diagnostics](dns_diagnostics/) |
| Workspace URL not accessible | [DNS Diagnostics](dns_diagnostics/) |
| Serverless can't reach storage | [Serverless Diagnostics](serverless_diagnostics/) |
| Package installs failing | [Serverless Diagnostics](serverless_diagnostics/) |
| Control plane connection issues | [DNS Diagnostics](dns_diagnostics/) |

---

## 💡 Best Practices

1. **Start with DNS Diagnostics** - Fastest test (30 seconds)
2. **Use appropriate compute** - Serverless script requires serverless compute
3. **Save JSON output** - For support tickets and documentation
4. **Compare environments** - Run on both serverless and classic compute
5. **Read individual READMEs** - Each script has detailed troubleshooting guide

---

## 🔗 Links

- **Main Repository**: https://github.com/prabakar2610/Databricks
- **Network Analysis Home**: [../](../)
- **Azure CLI Scripts**: [../azure_cli_scripts/](../azure_cli_scripts/)

---

**Version:** 4.0  
**Last Updated:** 2026-01-24  
**Organization:** Individual folders with dedicated READMEs
