# DNS Diagnostics

**DNS configuration and resolution testing for Azure Databricks**

## 📋 Overview

This script validates DNS resolution for Azure Databricks networking including workspace endpoints, control plane, storage accounts, and custom domains.

**Run Time:** ~30 seconds  
**Environment:** Databricks Notebook (any compute type)

---

## 🎯 When to Use

Use this script when you experience:

- ❌ Cannot access Databricks workspace URL
- ❌ Control plane connection issues
- ❌ Storage mount failures
- ❌ Custom domain not resolving
- ❌ DNS resolving to public instead of private IPs
- ❌ Need to verify DNS configuration

---

## 🚀 Usage

### **Method 1: Run from GitHub** (Recommended)

```python
# Optional: Configure custom domains and storage accounts
CUSTOM_DOMAINS = [
    "api.yourdomain.com",
    "db.yourdomain.com",
]
STORAGE_ACCOUNTS = [
    "yourstorageaccount",
]

# Download and run
import requests
URL = "https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/dns_diagnostics/script.py"
exec(requests.get(URL).text)
```

### **Method 2: Minimal Configuration** (Just Run It)

```python
# No configuration needed - auto-detects workspace
import requests
exec(requests.get("https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/dns_diagnostics/script.py").text)
```

### **Method 3: Copy and Paste**

1. Open `script.py` in this folder
2. Copy the entire script
3. Paste into a Databricks notebook cell
4. Optionally update configuration
5. Run the cell

---

## ⚙️ Configuration Parameters

### **Optional Parameters** (Auto-detected if not set)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `WORKSPACE_URL` | Databricks workspace URL | Auto-detected or `"adb-12345.azuredatabricks.net"` |
| `CUSTOM_DOMAINS` | Additional domains to test | `["api.example.com", "db.example.com"]` |
| `STORAGE_ACCOUNTS` | Storage account names | `["mystorageacct", "datalake"]` |
| `TEST_CONTROL_PLANE` | Test control plane endpoints | `True` (default) |

---

## 📊 What It Tests

### **1. Workspace DNS**
- 🏢 Workspace URL resolution
- 🏢 Private vs public IP detection
- 🏢 Resolution time

### **2. Control Plane Endpoints**
- 🎛️ Regional control plane URLs
- 🎛️ SCC relay endpoints
- 🎛️ Tunnel endpoints
- 🎛️ Metastore endpoints

### **3. Storage Account DNS**
- 💾 ADLS Gen2 (dfs.core.windows.net)
- 💾 Blob Storage (blob.core.windows.net)
- 💾 Private endpoint detection
- 💾 Resolution for each storage account

### **4. Custom Domains**
- 🌐 User-specified domain resolution
- 🌐 Private vs public IP detection
- 🌐 Resolution time analysis

### **5. External DNS (Baseline)**
- 🌍 Google DNS (8.8.8.8)
- 🌍 Verifies external connectivity
- 🌍 Baseline comparison

---

## 📤 Output

### **Console Output**

```
======================================================================
 Workspace DNS Resolution
======================================================================

✅ Workspace URL
  Domain: adb-12345.10.azuredatabricks.net
  IP: 10.139.64.10 (Private)
  Time: 0.012s

======================================================================
 Storage Account DNS
======================================================================

Testing: mystorageacct

✅ ADLS Gen2 (DFS)
  Domain: mystorageacct.dfs.core.windows.net
  IP: 10.0.5.4 (Private)
  Time: 0.015s

✅ Blob Storage
  Domain: mystorageacct.blob.core.windows.net
  IP: 10.0.5.5 (Private)
  Time: 0.013s

======================================================================
 Custom Domains
======================================================================

✅ api.yourdomain.com
  Domain: api.yourdomain.com
  IP: 10.0.1.100 (Private)
  Time: 0.018s

======================================================================
 Summary
======================================================================

✅ DNS Configuration: HEALTHY

Total Tests: 8
✅ Successful: 8
❌ Failed: 0

Private IPs: 8/8 (100%)
Public IPs: 0/8 (0%)
```

### **JSON Export**

Complete results in JSON format for automation and analysis.

---

## 🆘 Troubleshooting Common Issues

### **Issue 1: Workspace URL Resolves to Public IP**

**Symptom:**
```
⚠️ Workspace URL
  IP: 20.123.45.67 (Public)
```

**Possible Causes:**
1. Workspace Private Link not enabled
2. Private DNS Zone not linked
3. Running from outside VNet

**Solutions:**
- Enable workspace Private Link (Frontend or Backend)
- Link Private DNS Zone to VNet
- Verify notebook is running in correct network context

---

### **Issue 2: Storage Account Resolves to Public IP**

**Symptom:**
```
⚠️ ADLS Gen2 (DFS)
  IP: 52.123.45.67 (Public)
```

**Possible Causes:**
1. Storage account private endpoint not configured
2. Private DNS Zone not linked
3. DNS Zone for storage not created

**Solutions:**
- Create private endpoint for storage account
- Create/link Private DNS Zone for storage (privatelink.dfs.core.windows.net)
- Verify DNS Zone has A record for storage account

---

### **Issue 3: Custom Domain DNS Fails**

**Symptom:**
```
❌ api.yourdomain.com
  Error: [Errno -2] Name or service not known
```

**Possible Causes:**
1. Domain doesn't exist in Private DNS Zone
2. Typo in domain name
3. DNS Zone not linked to VNet
4. A record not created

**Solutions:**
- Create A record in Private DNS Zone
- Verify domain name spelling
- Link DNS Zone to Databricks VNet
- Check DNS Zone configuration

---

### **Issue 4: Control Plane Issues**

**Symptom:**
```
❌ Control Plane Endpoint
  Error: DNS resolution failed
```

**Possible Causes:**
1. Regional control plane connectivity blocked
2. DNS resolution to control plane failing
3. Network routing issue

**Solutions:**
- Check NSG rules for control plane connectivity
- Verify Azure Databricks service tags allowed
- Review UDR (User Defined Routes)
- Check firewall rules

---

## 📖 DNS Zone Names Reference

### **Databricks Private DNS Zones**

| Service | DNS Zone |
|---------|----------|
| Workspace Frontend | `privatelink.azuredatabricks.net` |
| Workspace Backend (UI API) | `privatelink.azuredatabricks.net` |
| Browser Auth | `privatelink.azuredatabricks.net` |

### **Storage Private DNS Zones**

| Service | DNS Zone |
|---------|----------|
| ADLS Gen2 (DFS) | `privatelink.dfs.core.windows.net` |
| Blob Storage | `privatelink.blob.core.windows.net` |
| File Storage | `privatelink.file.core.windows.net` |
| Table Storage | `privatelink.table.core.windows.net` |
| Queue Storage | `privatelink.queue.core.windows.net` |

---

## 💡 Tips

1. **Run this script first** - It's the fastest diagnostic (30 sec)
2. **No configuration needed** - Works out of the box for basic tests
3. **Auto-detects workspace** - Uses Databricks context
4. **Add custom domains** - Test your internal services
5. **Save JSON output** - For support tickets and documentation
6. **Re-run after DNS changes** - Verify configuration updates
7. **Compare compute types** - Run on both serverless and classic compute

---

## 🔍 Understanding Private vs Public IPs

### **Private IP Ranges** (RFC 1918)
- `10.0.0.0` - `10.255.255.255` (10.0.0.0/8)
- `172.16.0.0` - `172.31.255.255` (172.16.0.0/12)
- `192.168.0.0` - `192.168.255.255` (192.168.0.0/16)
- `100.64.0.0` - `100.127.255.255` (100.64.0.0/10) - Shared address space

### **What It Means**

**✅ Private IP**: DNS is correctly resolving through Private DNS Zone
- Traffic stays within your VNet
- Uses Private Link connection
- More secure and lower latency

**⚠️ Public IP**: DNS is resolving to public endpoint
- Traffic goes over internet
- Not using Private Link
- May be blocked by firewall/NSG

---

## 📖 Related Documentation

- [Azure Private DNS](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
- [Databricks Workspace Private Link](https://learn.microsoft.com/en-us/azure/databricks/security/network/classic/private-link)
- [Storage Private Endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [DNS Integration with Private Endpoints](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns)

---

## 🔗 Quick Links

- **Main Repository**: https://github.com/prabakar2610/Databricks
- **All Network Scripts**: [../](../)
- **Private Link Diagnostics**: [../private_link_diagnostics/](../private_link_diagnostics/)
- **Serverless Diagnostics**: [../serverless_diagnostics/](../serverless_diagnostics/)

---

**Version:** 3.0  
**Last Updated:** 2026-01-24  
**Script:** `script.py`
