# 📦 Complete Azure Private Link Troubleshooting Suite

## 🎯 What You Have

This directory contains a **complete, enterprise-grade troubleshooting suite** for diagnosing Azure Databricks Private Link connectivity issues where DNS resolves to public IPs instead of private IPs.

---

## 📁 All Files & Their Purpose

### **Core Diagnostic Scripts**

| File | Purpose | Run On | Time | Use Case |
|------|---------|--------|------|----------|
| `databricks_private_link_diagnostics.py` | Basic connectivity test | Databricks Notebook | 30s | Quick health check |
| `databricks_private_link_diagnostics_enhanced.py` ⭐ | **Comprehensive diagnostics** | Databricks Notebook | 2 min | Deep troubleshooting |
| `azure_vm_diagnostics.sh` | VM comparison test | Azure VM (Linux) | 1 min | Validate Azure infrastructure |
| `analyze_results.py` | Result analyzer | Local machine | Instant | Interpret JSON results |

### **Documentation**

| File | Purpose | When to Read |
|------|---------|-------------|
| `README.md` | Complete documentation | First read |
| `TROUBLESHOOTING_FLOWCHART.md` | Step-by-step troubleshooting guide | When you have issues |
| `CHEAT_SHEET.txt` | Quick reference card | Keep open while troubleshooting |
| `case.txt` | Original issue description | Background information |

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Run Databricks Test** (2 minutes)

1. Open Databricks notebook
2. Copy `databricks_private_link_diagnostics_enhanced.py`
3. Update configuration:
   ```python
   DOMAINS_TO_TEST = [
       {"host": "your-service.your-domain.com", "port": 443, "description": "Service Name"},
   ]
   PRIVATE_DNS_ZONE = "your-domain.com"
   NCC_DOMAIN = "your-domain.com"
   EXPECTED_PRIVATE_IP_PREFIX = "10.0"
   ```
4. Run the cell
5. **Save the JSON output**

### **Step 2: Interpret Results**

| Result | Status | Action |
|--------|--------|--------|
| All tests pass ✅ | Working! | No action needed |
| DNS → Public IP ❌ | **Most common issue** | Go to Section A below |
| DNS fails ❌ | Missing DNS record | Go to Section B below |
| DNS works, TCP fails ❌ | Backend issue | Go to Section C below |

### **Step 3: Follow Fix Instructions**

See quick fixes below or refer to `TROUBLESHOOTING_FLOWCHART.md` for detailed steps.

---

## 🔥 Common Issues & Quick Fixes

### **Section A: DNS Resolves to Public IP** (90% of issues)

**Symptom:**
```
❌ IP Type: PUBLIC IP - Private Link is NOT being used!
```

**Root Cause:** Private DNS Zone name ≠ NCC Domain name

**Quick Fix:**
1. Check if `PRIVATE_DNS_ZONE` = `NCC_DOMAIN` in your configuration
2. If they don't match exactly (character-for-character):
   - Go to Databricks Account Console
   - Edit Network Connectivity Config
   - Update Domain to match Private DNS Zone **exactly**
   - Save and wait 10 minutes
   - Restart Databricks cluster
   - Re-run test

**Common Mistakes:**
```
DNS Zone:  internal.contoso.com
NCC:       contoso.com              ❌ Missing subdomain
NCC:       https://internal...      ❌ Has protocol
NCC:       *.internal.contoso.com   ❌ Has wildcard
```

**Correct Format:**
```
DNS Zone:  internal.contoso.com
NCC:       internal.contoso.com     ✅ Exact match
```

---

### **Section B: DNS Resolution Failed**

**Symptom:**
```
❌ DNS resolution failed
```

**Quick Fix:**
```bash
# Check if DNS record exists
az network private-dns record-set a list \
  --zone-name <your-zone> \
  --resource-group <your-rg>

# If missing, add it
az network private-dns record-set a add-record \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --record-set-name <hostname> \
  --ipv4-address <lb-private-ip>
```

---

### **Section C: TCP Connection Failed**

**Symptom:**
```
✅ DNS Resolution: 10.0.1.100 (private IP)
❌ TCP Connection: Connection failed
```

**Good News:** Private Link DNS is working!

**Quick Checks:**
1. **Load Balancer health probe:**
   - Azure Portal → Load Balancer → Backend Pools
   - Check if targets are healthy
   
2. **NSG rules:**
   ```bash
   az network nsg rule list --nsg-name <nsg> --resource-group <rg>
   ```
   - Must allow traffic from Private Endpoint subnet
   
3. **Backend service:**
   ```bash
   ssh user@backend-vm
   sudo netstat -tlnp | grep <port>
   ```
   - Service must be running and listening

---

## 🎨 What Makes This Suite Special

### **Enhanced Databricks Script Features**

✨ **Comprehensive Diagnostics:**
- ✅ DNS reliability testing (5 attempts)
- ✅ TCP reliability testing (3 attempts)
- ✅ Port scanning (common ports)
- ✅ Latency breakdown (DNS vs TCP time)
- ✅ Pattern detection (same IP for all domains?)
- ✅ External connectivity test
- ✅ Egress IP detection
- ✅ Configuration validation

✨ **Intelligent Analysis:**
- Automatically detects root causes
- Provides specific recommendations
- Identifies configuration mismatches
- Warns about inconsistent DNS
- Flags unreliable connections

✨ **Professional Output:**
- Color-coded results (easy to read)
- Detailed timing metrics
- JSON export for support tickets
- Machine-readable results

### **Azure VM Script Features**

✨ **Multi-Tool DNS Testing:**
- `dig` (detailed analysis)
- `nslookup` (standard lookup)
- `host` (quick check)

✨ **Comprehensive Network Testing:**
- TCP connectivity tests
- Optional traceroute
- Optional port scanning (with nmap)
- Azure metadata inspection
- Firewall/security checks

✨ **Comparison Ready:**
- Output format matches Databricks test
- Easy to compare results
- Identifies infrastructure vs NCC issues

---

## 📊 Results Comparison Matrix

Run both scripts and compare:

| Databricks | Azure VM | Root Cause | Fix |
|------------|----------|------------|-----|
| Public IP ❌ | Public IP ❌ | DNS Zone misconfigured | Fix DNS Zone config |
| Public IP ❌ | Private IP ✅ | **NCC misconfigured** | Fix NCC Domain |
| DNS Fail ❌ | DNS Fail ❌ | Missing DNS record | Add A record |
| Private IP ✅, TCP Fail ❌ | Private IP ✅, TCP Fail ❌ | Backend/LB issue | Fix LB or NSG |
| Private IP ✅, TCP Fail ❌ | All Pass ✅ | NSG blocks Databricks | Fix NSG rules |
| All Pass ✅ | All Pass ✅ | Everything working! | 🎉 |

---

## 💡 Key Configuration Rules

### **Domain Names**

**In DOMAINS_TO_TEST:**
```python
✅ CORRECT:   "api.internal.contoso.com"
❌ WRONG:     "https://api.internal.contoso.com"  # No protocol
❌ WRONG:     "*.internal.contoso.com"            # No wildcards
❌ WRONG:     "api"                                # Must be FQDN
```

### **Private DNS Zone**

**In PRIVATE_DNS_ZONE:**
```python
✅ CORRECT:   "internal.contoso.com"              # Zone suffix only
❌ WRONG:     "api.internal.contoso.com"          # No specific hostname
❌ WRONG:     "https://internal.contoso.com"      # No protocol
```

### **NCC Domain** (Most Critical!)

**In NCC_DOMAIN (and Databricks Console):**
```python
✅ CORRECT:   "internal.contoso.com"              # Zone name only

❌ WRONG:     "https://internal.contoso.com"      # No protocol
❌ WRONG:     "*.internal.contoso.com"            # No wildcards
❌ WRONG:     "api.internal.contoso.com"          # No hostname
❌ WRONG:     "internal.contoso.com/"             # No trailing slash

🔥 MUST match Private DNS Zone name EXACTLY!
```

---

## 🛠️ Useful Commands Reference

### **Diagnostic Commands**

```bash
# List DNS Zones
az network private-dns zone list --resource-group <rg> --output table

# List DNS A records
az network private-dns record-set a list \
  --zone-name <zone> --resource-group <rg> --output table

# Show Private Endpoint
az network private-endpoint show \
  --name <pe-name> --resource-group <rg>

# Check Load Balancer
az network lb show \
  --name <lb-name> --resource-group <rg>

# List NSG rules
az network nsg rule list \
  --nsg-name <nsg> --resource-group <rg> --output table
```

### **Fix Commands**

```bash
# Add DNS A record
az network private-dns record-set a add-record \
  --resource-group <rg> \
  --zone-name <zone> \
  --record-set-name <hostname> \
  --ipv4-address <ip>

# Create VNet link
az network private-dns link vnet create \
  --resource-group <rg> \
  --zone-name <zone> \
  --name <link-name> \
  --virtual-network <vnet-id> \
  --registration-enabled false

# Add NSG rule
az network nsg rule create \
  --resource-group <rg> \
  --nsg-name <nsg> \
  --name AllowPrivateEndpoint \
  --priority 100 \
  --direction Inbound \
  --source-address-prefixes <pe-subnet-cidr> \
  --destination-port-ranges <port> \
  --protocol Tcp \
  --access Allow
```

---

## 📈 Advanced Usage

### **Enable All Diagnostic Features**

In `databricks_private_link_diagnostics_enhanced.py`:

```python
ENABLE_PORT_SCANNING = True
ENABLE_MULTIPLE_RESOLUTION_TESTS = True
ENABLE_LATENCY_ANALYSIS = True
ENABLE_EXTERNAL_CONNECTIVITY_TEST = True

DNS_RETRY_COUNT = 10     # More thorough DNS testing
TCP_RETRY_COUNT = 5      # More thorough TCP testing
```

### **Enable Advanced VM Diagnostics**

In `azure_vm_diagnostics.sh`:

```bash
ENABLE_ADVANCED_DIAGNOSTICS=true

# Requires: nmap, tcptraceroute, mtr
# Ubuntu: sudo apt-get install nmap tcptraceroute mtr
# RHEL: sudo yum install nmap traceroute mtr
```

### **Analyze Results Programmatically**

```bash
# Save JSON from Databricks test
cat > results.json
# Paste JSON, then Ctrl+D

# Analyze
python analyze_results.py < results.json
```

---

## 📞 When to Contact Support

Contact support if:

- ✅ All configuration verified correct
- ✅ Both Databricks and Azure VM tests run
- ✅ Followed troubleshooting flowchart
- ✅ Waited 24 hours after making changes
- ❌ Still not working

**Provide to Support:**
1. JSON output from Databricks enhanced test
2. Full output from Azure VM test
3. Screenshots of NCC configuration (from Databricks console)
4. Screenshots of Private DNS Zone configuration (from Azure Portal)
5. Azure resource IDs (subscription, resource group, all resource names)

---

## 🎓 Learning Resources

### **Understanding the Architecture**

```
Databricks Serverless
    ↓ (Private Link)
Microsoft-managed VNet
    ↓ (Private Endpoint)
Your VNet
    ↓ (Internal Load Balancer)
Your Backend VMs
```

**Key Point:** Databricks doesn't use your VNet's DNS directly. Instead, it injects DNS overrides based on:
1. NCC Domain configuration
2. Private Endpoint + Private DNS Zone
3. Validated Private Link resource

**If DNS resolves to public IP from Databricks:**
→ Databricks hasn't accepted the domain for private routing
→ Usually means NCC Domain ≠ Private DNS Zone name

### **How Private DNS Works**

1. You create Private DNS Zone: `internal.contoso.com`
2. You add A record: `api.internal.contoso.com` → `10.0.1.100`
3. You link the zone to your VNet
4. Resources in the VNet now resolve `api.internal.contoso.com` to `10.0.1.100`

**For Databricks:**
- You ALSO configure NCC with domain `internal.contoso.com`
- Databricks internally routes queries for `*.internal.contoso.com` through Private Link
- This only works if NCC Domain matches the DNS Zone exactly

---

## 📚 Additional Documentation

- **Quick Start:** See `CHEAT_SHEET.txt`
- **Full Guide:** See `README.md`
- **Troubleshooting:** See `TROUBLESHOOTING_FLOWCHART.md`
- **Original Issue:** See `case.txt`

---

## 🎯 Success Criteria

You'll know everything is working when:

✅ **DNS Resolution:**
- Resolves to private IP (10.x.x.x, 172.16-31.x.x, or 192.168.x.x)
- Consistent across multiple attempts
- Fast (< 50ms)

✅ **TCP Connection:**
- Succeeds on first attempt
- Consistent across multiple attempts
- Fast (< 200ms)

✅ **Configuration:**
- Private DNS Zone name = NCC Domain name
- DNS A record points to Load Balancer private IP
- VNet link is active
- Private Endpoint is "Established"

---

## 🏆 Most Common Fix (90% of Cases)

**Issue:** DNS resolves to public IP

**Fix:** Make sure these match EXACTLY:

```
Private DNS Zone:  internal.contoso.com
NCC Domain:        internal.contoso.com
                   ↑ Must be identical!
```

**Steps:**
1. Go to Databricks Account Console
2. Cloud Resources → Network Connectivity Configs
3. Edit your NCC
4. Update "Domain" field to match Private DNS Zone exactly
5. No protocol, no wildcards, no hostname - just the zone name
6. Save
7. Wait 10 minutes
8. Restart Databricks cluster
9. Re-run test

---

## 📝 Version Information

- **Created:** 2026-01-23
- **Suite Version:** 2.0
- **Scripts:** Python 3.7+ (Databricks), Bash (Azure VM)
- **Tested On:** Azure Databricks, Ubuntu/RHEL Azure VMs

---

## ✨ Summary

You now have:

1. ✅ **Two diagnostic scripts** (Databricks + Azure VM)
2. ✅ **Result analyzer** (Python tool)
3. ✅ **Complete documentation** (README, Flowchart, Cheat Sheet)
4. ✅ **All necessary commands** (Azure CLI reference)
5. ✅ **Troubleshooting guide** (Step-by-step fixes)

**Next Steps:**
1. Read `CHEAT_SHEET.txt` (2 minutes)
2. Run `databricks_private_link_diagnostics_enhanced.py` (2 minutes)
3. If issues, follow `TROUBLESHOOTING_FLOWCHART.md`
4. Run `azure_vm_diagnostics.sh` for comparison (optional)

**Good luck!** 🚀

Remember: 90% of issues are solved by ensuring `Private DNS Zone = NCC Domain` (exactly!)
