# Databricks Notebooks - Network Diagnostics Scripts

This folder contains modular network diagnostic scripts designed to run in **Databricks Notebooks**.

## 📋 Available Scripts

### 1. **01_private_link_diagnostics.py** ⭐
**Comprehensive Private Link diagnostics for internal resources**

**Use Case:** Troubleshoot Private Link connectivity to resources behind a load balancer in your VNet

**Tests:**
- DNS resolution (private vs public)
- TCP connectivity
- DNS reliability (multiple attempts)
- TCP reliability  
- Port scanning
- Latency breakdown
- Configuration validation

**Time:** ~2 minutes

**Configuration Required:**
- Domain names to test
- Private DNS Zone name
- NCC Domain name
- Expected IP ranges

---

### 2. **02_dns_diagnostics.py**
**DNS configuration and resolution testing**

**Use Case:** Validate DNS resolution for workspace, control plane, storage, and custom domains

**Tests:**
- Workspace DNS resolution
- Control plane endpoints
- Storage account DNS (ADLS Gen2, Blob)
- Custom domain resolution
- External DNS (baseline)
- Private vs Public IP detection

**Time:** ~30 seconds

**Configuration Required:**
- Storage account names (optional)
- Custom domains (optional)

---

### 3. **03_serverless_diagnostics.py**
**Serverless compute networking validation**

**Use Case:** Test serverless compute connectivity to storage, external services, and internal resources

**Tests:**
- Serverless to Azure Storage
- External connectivity (egress)
- Network policy validation
- Serverless Private Link
- Egress IP detection

**Time:** ~1 minute

**Configuration Required:**
- Storage accounts
- Private Link endpoints (optional)

---

## 🚀 How to Use

### **Method 1: Run from GitHub** (Recommended)

```python
# Configuration
DOMAINS_TO_TEST = [
    {"host": "api.yourdomain.com", "port": 443, "description": "API"},
]
PRIVATE_DNS_ZONE = "yourdomain.com"
NCC_DOMAIN = "yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

# Download and run
import requests
URL = "https://raw.githubusercontent.com/prabakar2610/Databricks/master/pvtlink_network_analysis/databricks_notebooks/01_private_link_diagnostics.py"
exec(requests.get(URL).text)
```

### **Method 2: Copy-Paste**

1. Open the script file
2. Copy entire contents
3. Paste into a Databricks notebook cell
4. Update configuration section
5. Run the cell

---

## 📊 When to Use Each Script

| Scenario | Use This Script |
|----------|----------------|
| Can't connect to internal API/database | `01_private_link_diagnostics.py` |
| DNS not resolving correctly | `02_dns_diagnostics.py` |
| Serverless can't reach storage | `03_serverless_diagnostics.py` |
| Package installs failing | `03_serverless_diagnostics.py` |
| Workspace URL not accessible | `02_dns_diagnostics.py` |
| Control plane connection issues | `02_dns_diagnostics.py` |

---

## 🎯 Script Comparison

| Feature | Private Link | DNS | Serverless |
|---------|-------------|-----|------------|
| DNS Testing | ✅ Deep | ✅ Comprehensive | ✅ Basic |
| TCP Testing | ✅ Detailed | ❌ | ✅ Basic |
| Reliability Testing | ✅ | ❌ | ❌ |
| Port Scanning | ✅ | ❌ | ❌ |
| Egress Testing | ❌ | ❌ | ✅ |
| Storage Testing | ❌ | ✅ DNS only | ✅ Full |
| Configuration Validation | ✅ | ❌ | ❌ |

---

## 💡 Tips

1. **Start with DNS diagnostics** (`02`) to verify basic connectivity
2. **Use Private Link diagnostics** (`01`) for internal resource issues
3. **Use Serverless diagnostics** (`03`) specifically on serverless compute
4. **Save JSON output** from each test for comparison and support tickets
5. **Run tests from different compute types** to isolate issues

---

## 🔧 Common Configuration

All scripts support these common patterns:

```python
# Storage accounts
STORAGE_ACCOUNTS = [
    {"name": "yourstorageaccount", "type": "adls_gen2"},
]

# Custom endpoints
CUSTOM_ENDPOINTS = [
    {"host": "api.yourdomain.com", "port": 443, "description": "API"},
]

# Network configuration
NETWORK_CONFIG = {
    "vnet_injected": False,
    "frontend_private_link_enabled": False,
    "backend_private_link_enabled": False,
}
```

---

## 📖 Reference Documentation

- [Azure Databricks Networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/)
- [Private Link Setup](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/pl-to-internal-network)
- [Serverless Networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/)

---

## 🆘 Troubleshooting

**Script fails to run:**
- Check you're running in correct compute context
- Verify Python version compatibility
- Check for typos in configuration

**No results shown:**
- Check configuration variables are set before running
- Verify network connectivity from notebook
- Try simpler test first (DNS diagnostics)

**Permission errors:**
- Some tests require network access
- Check workspace IP access lists
- Verify firewall rules

---

**All scripts output JSON** for easy parsing and automation!
