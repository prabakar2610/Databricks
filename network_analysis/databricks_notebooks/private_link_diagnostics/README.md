# Private Link Diagnostics

**Comprehensive Private Link connectivity diagnostics for Azure Databricks**

## 📋 Overview

This script provides deep diagnostics for Private Link connectivity issues when connecting from Azure Databricks to internal resources behind a load balancer in your VNet.

**Run Time:** ~2 minutes  
**Environment:** Databricks Notebook (any compute type)

---

## 🎯 When to Use

Use this script when you experience:

- ❌ Cannot connect to internal API/database from Databricks
- ❌ DNS resolves to public IP instead of private IP
- ❌ Timeout errors when accessing internal resources
- ❌ Intermittent connectivity to internal services
- ❌ Need to validate Private Link configuration

---

## 🚀 Usage

### **Method 1: Run from GitHub** (Recommended)

```python
# Configuration
DOMAINS_TO_TEST = [
    {"host": "api.yourdomain.com", "port": 443, "description": "API Service HTTPS"},
    {"host": "db.yourdomain.com", "port": 5432, "description": "PostgreSQL Database"},
]
PRIVATE_DNS_ZONE = "yourdomain.com"
NCC_DOMAIN = "yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"  # First 2 octets of your private IP range

# Download and run
import requests
URL = "https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/private_link_diagnostics/script.py"
exec(requests.get(URL).text)
```

### **Method 2: Copy and Paste**

1. Open `script.py` in this folder
2. Copy the entire script
3. Paste into a new Databricks notebook cell
4. Update the configuration section at the top
5. Run the cell

---

## ⚙️ Configuration Parameters

### **Required Parameters**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `DOMAINS_TO_TEST` | List of endpoints to test | `[{"host": "api.example.com", "port": 443, "description": "API"}]` |
| `PRIVATE_DNS_ZONE` | Your Azure Private DNS Zone name | `"internal.example.com"` |
| `NCC_DOMAIN` | Domain configured in Databricks NCC | `"internal.example.com"` |
| `EXPECTED_PRIVATE_IP_PREFIX` | First 2 octets of private IP | `"10.0"` or `"172.16"` |

### **Optional Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EXPECTED_LB_PRIVATE_IP` | `"10.0.1.100"` | Load balancer frontend IP (if known) |
| `DNS_RETRY_COUNT` | `5` | Number of DNS resolution attempts |
| `TCP_RETRY_COUNT` | `3` | Number of TCP connection attempts |
| `CONNECTION_TIMEOUT` | `5` | Timeout in seconds |
| `ENABLE_PORT_SCANNING` | `True` | Scan additional common ports |
| `ENABLE_MULTIPLE_RESOLUTION_TESTS` | `True` | Test DNS consistency |
| `ENABLE_LATENCY_ANALYSIS` | `True` | Measure connection latency |
| `ENABLE_EXTERNAL_CONNECTIVITY_TEST` | `True` | Test external connectivity baseline |

---

## 📊 What It Tests

### **1. Configuration Validation**
- ✅ DNS Zone matches NCC Domain
- ✅ Hostnames match DNS zone suffix
- ✅ Configuration consistency

### **2. DNS Diagnostics**
- 🔍 DNS resolution to private vs public IP
- 🔍 DNS resolution consistency (multiple attempts)
- 🔍 DNS resolution time
- 🔍 DNS reliability

### **3. TCP Connectivity**
- 🔌 TCP connection success/failure
- 🔌 Connection timeout detection
- 🔌 Connection reliability
- 🔌 Connection time analysis

### **4. Port Scanning**
- 🔎 Scan common ports (80, 443, 8080, etc.)
- 🔎 Identify open vs closed ports
- 🔎 Detect filtered ports

### **5. Latency Analysis**
- ⏱️ DNS resolution time
- ⏱️ TCP handshake time
- ⏱️ Total connection time
- ⏱️ Performance comparison

### **6. Comparative Analysis**
- 📈 Compare results across multiple domains
- 📈 Identify patterns in failures
- 📈 Root cause analysis

---

## 📤 Output

The script provides:

1. **Console Output**: Formatted, color-coded results with emojis
2. **JSON Export**: Complete results in JSON format for further analysis
3. **Summary Analysis**: Pattern detection and recommendations

### **Sample Output**

```
================================================================================
 DNS Resolution Test - api.yourdomain.com
================================================================================

✅ DNS resolved successfully
  Hostname: api.yourdomain.com
  IP Address: 10.0.1.100
  ✅ Resolves to PRIVATE IP (expected) ✓
  Resolution time: 0.023s

================================================================================
 TCP Connectivity Test - api.yourdomain.com:443
================================================================================

✅ TCP connection successful
  Target: 10.0.1.100:443
  Connection time: 0.145s
  Status: CONNECTED ✓

================================================================================
 Summary & Analysis
================================================================================

Overall Status: ✅ ALL TESTS PASSED

Configuration: VALID ✓
DNS Resolution: 2/2 successful (100%)
TCP Connectivity: 2/2 successful (100%)
```

---

## 🆘 Troubleshooting Common Issues

### **Issue 1: DNS Resolves to Public IP**

**Symptom:**
```
❌ Resolves to PUBLIC IP (10.x.x.x expected)
IP Address: 20.123.45.67
```

**Possible Causes:**
1. Private DNS Zone not linked to Databricks VNet
2. Domain not registered in Private DNS Zone
3. NCC configuration incorrect or missing
4. Typo in domain name

**Solutions:**
- Verify Private DNS Zone link in Azure Portal
- Check DNS Zone has A record for the domain
- Verify NCC Domain matches Private DNS Zone
- Check for typos in domain names

---

### **Issue 2: TCP Connection Timeout**

**Symptom:**
```
❌ TCP connection failed
Error: [Errno 110] Connection timed out
```

**Possible Causes:**
1. NSG blocking traffic
2. Load balancer not configured correctly
3. Backend service not running
4. Firewall rules blocking connection

**Solutions:**
- Check NSG rules on Databricks subnet
- Verify load balancer backend pool health
- Check backend service is running and listening
- Review firewall rules

---

### **Issue 3: Intermittent Failures**

**Symptom:**
```
⚠️ DNS resolution reliability: 3/5 successful (60%)
```

**Possible Causes:**
1. DNS caching issues
2. Load balancer health probe failing
3. Backend instances unhealthy
4. Network instability

**Solutions:**
- Check load balancer health probe status
- Verify backend instance health
- Review DNS TTL settings
- Check network logs for packet loss

---

## 📖 Related Documentation

- [Azure Databricks Private Link](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/pl-to-internal-network)
- [Azure Private DNS](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
- [Network Connectivity Configuration (NCC)](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/network-connectivity-config)
- [Azure Load Balancer](https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-overview)

---

## 💡 Tips

1. **Run on serverless compute** to test serverless Private Link connectivity
2. **Run on classic compute** to test VNet injection connectivity
3. **Compare results** between serverless and classic compute
4. **Save JSON output** for support tickets and documentation
5. **Test multiple ports** to identify port-specific issues
6. **Re-run after changes** to validate fixes

---

## 🔗 Quick Links

- **Main Repository**: https://github.com/prabakar2610/Databricks
- **All Network Scripts**: [../](../)
- **Azure CLI Comparison**: [../../azure_cli_scripts/private_link_validation/](../../azure_cli_scripts/private_link_validation/)

---

**Version:** 3.0  
**Last Updated:** 2026-01-24  
**Script:** `script.py`
