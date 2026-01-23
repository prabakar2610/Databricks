# Serverless Diagnostics

**Serverless compute networking validation for Azure Databricks**

## 📋 Overview

This script validates serverless compute connectivity to Azure Storage, external services, and internal resources via Private Link. It helps diagnose networking issues specific to Databricks serverless compute.

**Run Time:** ~1 minute  
**Environment:** Databricks Notebook (Serverless SQL Warehouse or Serverless Jobs)  
**⚠️ Important:** Must run on serverless compute for accurate results!

---

## 🎯 When to Use

Use this script when you experience:

- ❌ Serverless cannot access storage accounts
- ❌ Package installation failures (PyPI, apt, etc.)
- ❌ External API calls timing out
- ❌ Serverless Private Link connectivity issues
- ❌ Need to validate serverless network configuration
- ❌ Egress connectivity problems

---

## 🚀 Usage

### **Method 1: Run from GitHub** (Recommended)

```python
# Configuration
STORAGE_ACCOUNTS = [
    {
        "name": "yourstorageaccount",
        "test_adls": True,
        "test_blob": True,
    },
]

PRIVATE_LINK_ENDPOINTS = [
    {"host": "api.yourdomain.com", "port": 443, "description": "Internal API"},
]

# Download and run
import requests
URL = "https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/serverless_diagnostics/script.py"
exec(requests.get(URL).text)
```

### **Method 2: Minimal Test** (Default Settings)

```python
# Run with default external services test
import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/serverless_diagnostics/script.py").text)
```

### **Method 3: Copy and Paste**

1. Open `script.py` in this folder
2. Copy the entire script
3. Create a serverless SQL Warehouse or serverless job cluster
4. Paste script into a notebook cell
5. Update configuration
6. Run the cell

---

## ⚙️ Configuration Parameters

### **Storage Accounts**

```python
STORAGE_ACCOUNTS = [
    {
        "name": "mystorageaccount",      # Storage account name
        "test_adls": True,                # Test ADLS Gen2 (DFS)
        "test_blob": True,                # Test Blob Storage
    },
]
```

### **External Services** (Default)

```python
EXTERNAL_SERVICES = [
    {"host": "pypi.org", "port": 443, "description": "PyPI (Python packages)"},
    {"host": "packages.microsoft.com", "port": 443, "description": "Microsoft packages"},
    {"host": "archive.ubuntu.com", "port": 80, "description": "Ubuntu packages"},
    {"host": "aka.ms", "port": 443, "description": "Microsoft redirects"},
]
```

### **Private Link Endpoints**

```python
PRIVATE_LINK_ENDPOINTS = [
    {"host": "api.yourdomain.com", "port": 443, "description": "Internal API"},
    {"host": "db.yourdomain.com", "port": 5432, "description": "PostgreSQL DB"},
]
```

---

## 📊 What It Tests

### **1. Compute Type Detection**
- 🖥️ Verifies running on serverless compute
- 🖥️ Warns if running on classic compute
- 🖥️ Provides context for test results

### **2. Storage Connectivity**
- 💾 ADLS Gen2 (DFS) DNS resolution
- 💾 Blob Storage DNS resolution
- 💾 TCP connectivity to storage endpoints
- 💾 Private vs public IP detection
- 💾 Connection time analysis

### **3. External Connectivity (Egress)**
- 🌍 PyPI connectivity (Python packages)
- 🌍 Microsoft package repositories
- 🌍 Ubuntu package repositories
- 🌍 DNS resolution
- 🌍 TCP connectivity

### **4. Private Link Endpoints**
- 🔒 Custom domain DNS resolution
- 🔒 TCP connectivity to internal resources
- 🔒 Private IP validation
- 🔒 Connection reliability

### **5. Network Policy Validation**
- 🛡️ Detects network restrictions
- 🛡️ Identifies egress blocks
- 🛡️ Firewall rule analysis

---

## 📤 Output

### **Console Output**

```
======================================================================
 Serverless Compute Detection
======================================================================

✅ Running on Serverless compute

======================================================================
 Storage Account Connectivity: mystorageaccount
======================================================================

Testing ADLS Gen2 (DFS)...

✅ DNS Resolution
  Domain: mystorageaccount.dfs.core.windows.net
  IP: 10.0.5.4 (Private)
  Time: 0.015s

✅ TCP Connectivity
  Target: 10.0.5.4:443
  Status: Connected
  Time: 0.098s

======================================================================
 External Connectivity (Egress)
======================================================================

Testing: pypi.org:443

✅ DNS Resolution
  IP: 151.101.0.223
  Time: 0.025s

✅ TCP Connectivity
  Status: Connected
  Time: 0.145s

======================================================================
 Private Link Endpoints
======================================================================

Testing: api.yourdomain.com:443

✅ DNS Resolution
  IP: 10.0.1.100 (Private)
  Time: 0.012s

✅ TCP Connectivity
  Status: Connected
  Time: 0.089s

======================================================================
 Summary
======================================================================

✅ Serverless Networking: HEALTHY

Compute Type: Serverless ✓
Storage Tests: 2/2 successful (100%)
External Tests: 4/4 successful (100%)
Private Link Tests: 1/1 successful (100%)
```

### **JSON Export**

Complete results in JSON format for automation.

---

## 🆘 Troubleshooting Common Issues

### **Issue 1: Not Running on Serverless**

**Symptom:**
```
⚠️ May not be running on serverless compute
   Results may not reflect serverless networking
```

**Solution:**
- Create a serverless SQL Warehouse
- OR create a serverless job cluster
- Run the script on that compute

**How to Create Serverless Compute:**
1. Go to SQL Warehouses
2. Click "Create SQL Warehouse"
3. Select "Serverless" type
4. Or use serverless job cluster in workflow

---

### **Issue 2: Storage Access Blocked**

**Symptom:**
```
❌ TCP Connectivity
  Error: [Errno 110] Connection timed out
```

**Possible Causes:**
1. Storage account firewall blocking serverless IPs
2. Storage private endpoint not accessible to serverless
3. Network security restrictions

**Solutions:**
- **Option A**: Allow serverless egress IPs in storage firewall
- **Option B**: Use serverless Private Link to storage
- **Option C**: Disable storage firewall (not recommended for production)
- Verify storage account network settings in Azure Portal

---

### **Issue 3: External Access Blocked**

**Symptom:**
```
⚠️ External access blocked: 4/4 services

   Possible causes:
   • Network policies restricting egress
   • Firewall rules
   • Service-specific blocks
```

**Possible Causes:**
1. Workspace-level network policies
2. Azure Firewall blocking egress
3. Private endpoint policies
4. Service endpoint policies

**Solutions:**
- Review workspace network configuration
- Check if NCC (Network Connectivity Config) is blocking egress
- Verify Azure Firewall rules
- Check service endpoint policies on VNet

**To Allow Specific External Services:**
- Update workspace network configuration
- Add allowed FQDNs to firewall
- Configure service endpoints

---

### **Issue 4: Private Link Endpoint Unreachable**

**Symptom:**
```
❌ DNS Resolution
  Error: [Errno -2] Name or service not known
```

**Possible Causes:**
1. Serverless Private Link (NCC) not configured
2. Domain not in Private DNS Zone
3. Private DNS Zone not accessible
4. NCC Domain mismatch

**Solutions:**
- Create Network Connectivity Config (NCC) in Databricks
- Add domain to Private DNS Zone
- Link Private DNS Zone to NCC VNet
- Verify NCC Domain configuration

**NCC Configuration:**
```
Databricks Workspace Settings
→ Network Connectivity Configuration
→ Create NCC
→ Specify VNet with Private DNS Zone
→ Add domain to allowed list
```

---

## 📖 Understanding Serverless Networking

### **Serverless Compute Networking Model**

```
┌─────────────────────────────────────────┐
│   Serverless Compute (Microsoft VNet)   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │   Your Databricks Notebook       │   │
│  └──────────────────────────────────┘   │
│              │                           │
│              ▼                           │
│  ┌──────────────────────────────────┐   │
│  │   Egress Path                    │   │
│  │   • Direct to Internet           │   │
│  │   • Or via Private Link (NCC)    │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                │
                ▼
    ┌───────────────────────┐
    │   Public Internet     │ ◄── Default
    │   or                  │
    │   Your VNet via NCC   │ ◄── With Private Link
    └───────────────────────┘
```

### **Key Differences from Classic Compute**

| Aspect | Classic Compute | Serverless |
|--------|----------------|------------|
| **VNet** | Customer VNet | Microsoft VNet |
| **Private Link** | VNet Injection | NCC (Network Connectivity Config) |
| **Storage Access** | Direct via VNet | Via public or NCC Private Link |
| **External Access** | NSG controlled | Workspace policies + NCC |
| **Egress IPs** | Customer NAT | Microsoft NAT (dynamic) |

---

## 💡 Tips

1. **Run on serverless compute** - Results only valid on serverless
2. **Test storage first** - Most common serverless issue
3. **Check external access** - Package installs depend on this
4. **Use NCC for internal resources** - Required for serverless Private Link
5. **Save JSON output** - For support tickets
6. **Compare with classic compute** - Run similar tests on classic cluster
7. **Test after NCC changes** - Verify configuration updates

---

## 🔍 Common Serverless Use Cases

### **Use Case 1: Storage Access**
```python
STORAGE_ACCOUNTS = [
    {"name": "datalake", "test_adls": True, "test_blob": False},
]
```
Run to verify ADLS Gen2 connectivity for data access.

### **Use Case 2: Package Installation**
```python
# Use default EXTERNAL_SERVICES
# Tests PyPI, apt repositories
```
Run to diagnose pip install or apt-get failures.

### **Use Case 3: Internal API Access**
```python
PRIVATE_LINK_ENDPOINTS = [
    {"host": "api.internal.com", "port": 443, "description": "Internal API"},
]
```
Run to verify serverless can reach internal services.

---

## 📖 Related Documentation

- [Serverless Network Security](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/)
- [Network Connectivity Config (NCC)](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/network-connectivity-config)
- [Serverless Private Link](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/pl-to-internal-network)
- [Serverless SQL Warehouses](https://learn.microsoft.com/en-us/azure/databricks/sql/admin/sql-endpoints)

---

## 🔗 Quick Links

- **Main Repository**: https://github.com/prabakar2610/Databricks
- **All Network Scripts**: [../](../)
- **DNS Diagnostics**: [../dns_diagnostics/](../dns_diagnostics/)
- **Private Link Diagnostics**: [../private_link_diagnostics/](../private_link_diagnostics/)

---

**Version:** 3.0  
**Last Updated:** 2026-01-24  
**Script:** `script.py`  
**⚠️ Must run on serverless compute!**
