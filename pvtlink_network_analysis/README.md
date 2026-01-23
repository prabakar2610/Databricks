# Azure Private Link Diagnostics - Complete Testing Suite

This directory contains a comprehensive testing suite for diagnosing Azure Databricks Private Link connectivity issues.

## 📁 Files Overview

### 1. `databricks_private_link_diagnostics.py`
**Basic Databricks diagnostics** - Simple, focused connectivity tests
- **Use for:** Quick health checks
- **Run in:** Databricks notebook
- **Time:** ~30 seconds

### 2. `databricks_private_link_diagnostics_enhanced.py` ⭐
**Enhanced Databricks diagnostics** - Comprehensive analysis with advanced features
- **Use for:** Deep troubleshooting and reliability testing
- **Run in:** Databricks notebook
- **Time:** 1-3 minutes
- **Features:**
  - Multiple DNS resolution attempts (reliability testing)
  - Port scanning
  - Latency analysis
  - Pattern detection
  - TCP reliability testing
  - Detailed timing breakdowns

### 3. `azure_vm_diagnostics.sh`
**Azure VM diagnostics** - Companion script for comparison testing
- **Use for:** Validating Azure infrastructure from inside the VNet
- **Run on:** Azure VM in the same VNet as Private Endpoint
- **Time:** 1-2 minutes
- **Features:**
  - DNS resolution with multiple tools (dig, nslookup, host)
  - TCP connectivity tests
  - Network path analysis
  - Azure metadata inspection
  - Firewall/security checks

---

## 🚀 Quick Start Guide

### Step 1: Run Enhanced Databricks Test

1. Open a Databricks notebook
2. Copy contents of `databricks_private_link_diagnostics_enhanced.py`
3. Update the CONFIGURATION section:

```python
DOMAINS_TO_TEST = [
    {"host": "your-service.your-domain.com", "port": 443, "description": "Your Service"},
]

PRIVATE_DNS_ZONE = "your-domain.com"
NCC_DOMAIN = "your-domain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"
EXPECTED_LB_PRIVATE_IP = "10.0.1.100"  # Optional
```

4. Run the cell
5. Review the output and save the JSON export

### Step 2: Run Azure VM Test (for comparison)

1. SSH into an Azure VM in your Private VNet:
   ```bash
   ssh username@your-vm-ip
   ```

2. Copy the script to the VM:
   ```bash
   # From your local machine
   scp azure_vm_diagnostics.sh username@your-vm-ip:~/
   ```

3. Make it executable and edit configuration:
   ```bash
   chmod +x azure_vm_diagnostics.sh
   nano azure_vm_diagnostics.sh
   ```

4. Update the CONFIGURATION section:
   ```bash
   DOMAINS_TO_TEST=(
       "your-service.your-domain.com:443"
       "your-service.your-domain.com:80"
   )
   
   PRIVATE_DNS_ZONE="your-domain.com"
   EXPECTED_LB_IP="10.0.1.100"
   EXPECTED_IP_PREFIX="10.0"
   ```

5. Run the script:
   ```bash
   ./azure_vm_diagnostics.sh
   ```

6. Review the output

### Step 3: Compare Results

Use the comparison matrix below to interpret your results.

---

## 🔍 Results Comparison Matrix

| Scenario | Databricks Result | Azure VM Result | Root Cause | Action |
|----------|-------------------|-----------------|------------|--------|
| **1. Both Fail - Public IP** | DNS → Public IP ❌ | DNS → Public IP ❌ | Private DNS not configured | Check DNS Zone and VNet link |
| **2. Both Fail - DNS Error** | DNS Failed ❌ | DNS Failed ❌ | DNS record missing | Add A record in Private DNS Zone |
| **3. VM Works, Databricks Fails** | DNS → Public IP ❌ | DNS → Private IP ✅ | NCC misconfigured | Check NCC domain configuration |
| **4. Both Private IP, Both TCP Fail** | DNS ✅ TCP ❌ | DNS ✅ TCP ❌ | Backend/LB issue | Check Load Balancer & NSG |
| **5. VM Works, Databricks TCP Fails** | DNS ✅ TCP ❌ | DNS ✅ TCP ✅ | NSG blocking Databricks | Check NSG rules for Private Endpoint subnet |
| **6. Both Work** | All Pass ✅ | All Pass ✅ | Everything OK! | No action needed |
| **7. Databricks Works, VM Fails** | All Pass ✅ | TCP Fails ❌ | VM-specific issue | Check VM NSG, firewall |

---

## 📊 Understanding the Enhanced Databricks Test

### Key Features

#### 1. **DNS Reliability Testing**
- Resolves DNS multiple times (default: 5 attempts)
- Detects inconsistent DNS responses
- Measures resolution time statistics (avg, min, max)

**What it tells you:**
- ✅ Consistent resolution = Stable DNS configuration
- ❌ Inconsistent resolution = DNS load balancing issue or flapping

#### 2. **TCP Reliability Testing**
- Tests connection multiple times (default: 3 attempts)
- Measures connection time variations
- Detects intermittent failures

**What it tells you:**
- ✅ All connections succeed = Reliable service
- ❌ Some connections fail = Backend health issues or network instability

#### 3. **Port Scanning**
- Scans common ports (80, 443, 8080, 8443, etc.)
- Identifies which services are accessible
- Helps diagnose port-specific issues

**What it tells you:**
- Open ports = Services listening and accessible
- All closed = Possible NSG blocking or service down

#### 4. **Latency Analysis**
- Breaks down connection time into:
  - DNS lookup time
  - TCP connection time
  - Total time

**What it tells you:**
- High DNS time = DNS resolution slow
- High TCP time = Network latency or backend slow
- Consistent times = Stable performance

#### 5. **Pattern Detection**
- Analyzes if all domains resolve to same IP
- Detects NAT or misconfiguration patterns
- Identifies mixed public/private IP scenarios

**What it tells you:**
- Same IP for all domains = Possible NAT issue
- Mixed public/private = Configuration inconsistency

---

## 🔧 Configuration Tips

### For Both Scripts

**1. Domain Configuration**
- Use FQDNs (Fully Qualified Domain Names)
- Match the Private DNS Zone suffix exactly
- No protocols (http://, https://)
- No wildcards (*.domain.com)

**Example:**
```
✅ CORRECT: api.internal.yourdomain.com
❌ WRONG: https://api.internal.yourdomain.com
❌ WRONG: *.internal.yourdomain.com
❌ WRONG: api
```

**2. Private DNS Zone**
- Must match NCC Domain exactly
- Use zone suffix only (not full FQDN)

**Example:**
```
✅ CORRECT: internal.yourdomain.com
❌ WRONG: api.internal.yourdomain.com
❌ WRONG: yourdomain.com (if your services are under internal.yourdomain.com)
```

**3. Expected IP Range**
- Use first 2 octets of your VNet range
- Helps validate DNS is returning correct range

**Example:**
```
If VNet is 10.0.0.0/16: use "10.0"
If VNet is 172.16.0.0/12: use "172.16"
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Databricks Shows Public IP, Azure VM Shows Private IP

**Root Cause:** NCC not properly configured or not attached to workspace

**Fix:**
1. Verify NCC Domain matches Private DNS Zone name exactly
2. Check workspace is attached to NCC in Databricks console
3. Verify Private Endpoint status is "Established"
4. Restart Databricks cluster

### Issue 2: Both Show Private IP but TCP Connection Fails

**Root Cause:** Backend or Load Balancer issue

**Fix:**
1. Check Load Balancer health probe status:
   ```bash
   az network lb probe show --resource-group <rg> --lb-name <lb> --name <probe>
   ```
2. Verify backend pool has healthy targets
3. Check NSG rules allow traffic:
   ```bash
   az network nsg rule list --resource-group <rg> --nsg-name <nsg>
   ```
4. Verify service is running on backend VM:
   ```bash
   netstat -tlnp | grep <port>
   ```

### Issue 3: DNS Resolution Fails on Both

**Root Cause:** Missing DNS record

**Fix:**
1. Check DNS records exist:
   ```bash
   az network private-dns record-set a list --zone-name <zone> --resource-group <rg>
   ```
2. Add missing record:
   ```bash
   az network private-dns record-set a add-record \
     --resource-group <rg> \
     --zone-name <zone> \
     --record-set-name <hostname> \
     --ipv4-address <lb-private-ip>
   ```

### Issue 4: Inconsistent DNS Results

**Root Cause:** Multiple DNS servers or caching issues

**Fix:**
1. Check Private DNS Zone has only one A record per hostname
2. Clear DNS cache (Databricks: restart cluster)
3. Verify VNet link is active

### Issue 5: Enhanced Test Times Out

**Root Cause:** Configuration has too many domains or slow network

**Fix:**
1. Reduce `DNS_RETRY_COUNT` and `TCP_RETRY_COUNT`
2. Increase `CONNECTION_TIMEOUT`
3. Disable port scanning: `ENABLE_PORT_SCANNING = False`
4. Test fewer domains at once

---

## 📈 Advanced Usage

### Enable All Enhanced Features

```python
# In databricks_private_link_diagnostics_enhanced.py
ENABLE_PORT_SCANNING = True
ENABLE_MULTIPLE_RESOLUTION_TESTS = True
ENABLE_LATENCY_ANALYSIS = True
ENABLE_EXTERNAL_CONNECTIVITY_TEST = True

DNS_RETRY_COUNT = 10  # More thorough testing
TCP_RETRY_COUNT = 5
```

### Enable Advanced VM Diagnostics

```bash
# In azure_vm_diagnostics.sh
ENABLE_ADVANCED_DIAGNOSTICS=true
```

This requires additional tools:
```bash
# Ubuntu/Debian
sudo apt-get install nmap tcptraceroute mtr

# RHEL/CentOS
sudo yum install nmap traceroute mtr
```

### Save Results for Comparison

**Databricks:**
```python
# After running the enhanced test, save the JSON output
import json

# Copy the JSON output from the script
results = { ... }  # Paste JSON here

# Save to DBFS
with open("/dbfs/diagnostics_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

**Azure VM:**
```bash
# Redirect output to file
./azure_vm_diagnostics.sh > diagnostics_output.txt 2>&1

# Download from VM
# From your local machine:
scp username@your-vm-ip:~/diagnostics_output.txt ./
```

---

## 📞 Support Information

### When Opening Support Tickets

Include the following from both scripts:

1. **JSON export from Databricks enhanced test**
2. **Full output from Azure VM test**
3. **Configuration values used**
4. **Azure resource information:**
   - Subscription ID
   - Resource Group name
   - Private Endpoint name
   - Load Balancer name
   - Private DNS Zone name
   - Databricks workspace name

### Useful Azure CLI Commands for Support

```bash
# Get Private Endpoint details
az network private-endpoint show --name <pe-name> --resource-group <rg> --output json

# Get Private DNS Zone details
az network private-dns zone show --name <zone> --resource-group <rg> --output json

# Get DNS records
az network private-dns record-set a list --zone-name <zone> --resource-group <rg> --output table

# Get VNet links
az network private-dns link vnet list --zone-name <zone> --resource-group <rg> --output table

# Get Load Balancer details
az network lb show --name <lb-name> --resource-group <rg> --output json

# Get NSG rules
az network nsg rule list --nsg-name <nsg-name> --resource-group <rg> --output table
```

---

## 📚 Additional Resources

- [Azure Private Link Documentation](https://docs.microsoft.com/azure/private-link/)
- [Databricks Serverless Network Security](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/pl-to-internal-network)
- [Azure Private DNS Zones](https://docs.microsoft.com/azure/dns/private-dns-overview)
- [Troubleshooting Private Endpoints](https://docs.microsoft.com/azure/private-link/troubleshoot-private-endpoint-connectivity)

---

## 🔄 Version History

- **v2.0** - Enhanced version with comprehensive diagnostics
- **v1.0** - Basic diagnostics

---

## 📝 License

These scripts are provided as-is for troubleshooting purposes.
