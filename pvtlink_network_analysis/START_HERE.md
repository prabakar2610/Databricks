# Azure Private Link Troubleshooting Suite - Start Here! 👋

## 🎯 Welcome!

You have a complete troubleshooting suite for Azure Databricks Private Link connectivity issues. This guide will help you get started in **under 5 minutes**.

---

## 🚦 Quick Navigation

**Choose your path:**

### 🆕 **First Time User?** 
→ Start with **[CHEAT_SHEET.txt](./CHEAT_SHEET.txt)** (3-minute read)  
→ Then run the enhanced Databricks test

### 🔍 **Have Test Results?**
→ Use **[TROUBLESHOOTING_FLOWCHART.md](./TROUBLESHOOTING_FLOWCHART.md)** to diagnose

### 📚 **Want Full Documentation?**
→ Read **[README.md](./README.md)** for comprehensive guide

### ⚡ **Just Want to Run Tests?**
→ Use `databricks_private_link_diagnostics_enhanced.py` in Databricks  
→ Use `azure_vm_diagnostics.sh` on Azure VM

### 📊 **Need to Interpret JSON Results?**
→ Use `analyze_results.py` locally

---

## 📁 File Guide

### **START HERE** (Pick One)

| File | Best For | Time |
|------|----------|------|
| **[CHEAT_SHEET.txt](./CHEAT_SHEET.txt)** ⭐ | Quick reference while troubleshooting | 3 min read |
| **[SUMMARY.md](./SUMMARY.md)** | Overview of entire suite | 5 min read |
| **[README.md](./README.md)** | Complete documentation | 15 min read |

### **Diagnostic Scripts** (Run These)

| Script | Platform | Purpose | Time |
|--------|----------|---------|------|
| `databricks_private_link_diagnostics_enhanced.py` ⭐ | Databricks Notebook | Main diagnostic test | 2 min |
| `databricks_private_link_diagnostics.py` | Databricks Notebook | Basic test (quick check) | 30 sec |
| `azure_vm_diagnostics.sh` | Azure VM (Linux) | Comparison test | 1 min |
| `analyze_results.py` | Local (Python) | Result interpreter | Instant |

### **Troubleshooting Guides** (Read When You Have Issues)

| Guide | Use When | Detail Level |
|-------|----------|--------------|
| **[TROUBLESHOOTING_FLOWCHART.md](./TROUBLESHOOTING_FLOWCHART.md)** ⭐ | You have failing tests | Step-by-step |
| **[CHEAT_SHEET.txt](./CHEAT_SHEET.txt)** | You need quick fixes | Quick reference |
| **[README.md](./README.md)** | You want to understand everything | Comprehensive |

### **Reference**

| File | Contains |
|------|----------|
| `case.txt` | Original issue description |
| `SUMMARY.md` | Suite overview and features |

---

## 🚀 5-Minute Quick Start

### **Step 1: Run the Enhanced Databricks Test** (2 min)

**Option A: Run from GitHub** (Recommended - No copy-pasting!)

1. Upload `databricks_private_link_diagnostics_enhanced.py` to your GitHub repo
2. In Databricks notebook, paste this code:

```python
# Configuration
DOMAINS_TO_TEST = [
    {"host": "your-service.yourdomain.com", "port": 443, "description": "My Service"},
]
PRIVATE_DNS_ZONE = "yourdomain.com"
NCC_DOMAIN = "yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

# Download and run from GitHub
import requests
URL = "https://raw.githubusercontent.com/YOUR-USER/YOUR-REPO/main/databricks_private_link_diagnostics_enhanced.py"
exec(requests.get(URL).text)
```

3. Update your GitHub URL and configuration values
4. Run the cell
5. **Save the JSON output** at the end

📘 **See `NOTEBOOK_QUICKSTART.txt` for detailed GitHub setup instructions**

---

**Option B: Copy-Paste Method** (Alternative)

1. Open a new Databricks notebook cell
2. Copy entire contents of `databricks_private_link_diagnostics_enhanced.py`
3. Update configuration section (lines 32-51)
4. Run the cell

### **Step 2: Check Results** (1 min)

Look for this in the output:

✅ **SUCCESS:**
```
✅ DNS Resolution: 10.0.1.100 (private IP)
✅ IP Type: Private IP (matches expected range)
✅ TCP Connection: Connection successful
Overall Status: ✅ ALL TESTS PASSED ✓
```
**Action:** Nothing! You're all set! 🎉

---

❌ **PROBLEM: Public IP**
```
❌ IP Type: PUBLIC IP - Private Link is NOT being used!
Overall Status: ❌ PRIVATE LINK NOT WORKING
```
**Action:** Go to "Quick Fix #1" below

---

❌ **PROBLEM: DNS Failed**
```
❌ DNS resolution failed
```
**Action:** Go to "Quick Fix #2" below

---

❌ **PROBLEM: TCP Failed**
```
✅ DNS Resolution: 10.0.1.100 (private IP)
❌ TCP Connection: Connection timeout
```
**Action:** Go to "Quick Fix #3" below

---

## ⚡ Quick Fixes

### **Quick Fix #1: Public IP Resolved** (Most Common - 90% of cases)

**The Issue:** DNS resolves to a public IP instead of private IP

**Most Common Cause:** Private DNS Zone name ≠ NCC Domain name

**The Fix:**
1. Check your diagnostic output:
   ```
   Configuration Validation:
     Private DNS Zone: internal.contoso.com
     NCC Domain:       internal.contoso.com
   ```
   
2. **Do they match EXACTLY?**
   - ✅ YES → See [TROUBLESHOOTING_FLOWCHART.md](./TROUBLESHOOTING_FLOWCHART.md) Section B
   - ❌ NO → **This is your problem!** Continue below:

3. **Fix the NCC Domain:**
   - Go to [Databricks Account Console](https://accounts.cloud.databricks.com)
   - Click "Cloud Resources" → "Network Connectivity Configs"
   - Edit your NCC
   - Update "Domain" field to match Private DNS Zone **exactly**
   - Remove any `https://`, `*.`, or specific hostnames
   - Just enter: `internal.contoso.com` (your zone name)
   - Save

4. **Apply the fix:**
   - Wait 10 minutes for changes to propagate
   - Go to your Databricks workspace
   - Restart your cluster
   - Re-run the diagnostic test

5. **Verify:** DNS should now resolve to private IP ✅

---

### **Quick Fix #2: DNS Failed**

**The Issue:** DNS resolution completely failed

**Quick Check:**
```bash
# Check if DNS record exists
az network private-dns record-set a list \
  --zone-name <your-zone> \
  --resource-group <your-rg> \
  --output table
```

**If record is missing:**
```bash
# Add the DNS record
az network private-dns record-set a add-record \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --record-set-name <hostname> \
  --ipv4-address <your-load-balancer-private-ip>
```

**Also check:** Spelling of domain name in your test configuration

For more details: [TROUBLESHOOTING_FLOWCHART.md](./TROUBLESHOOTING_FLOWCHART.md) Section A

---

### **Quick Fix #3: TCP Connection Failed**

**The Issue:** DNS works (resolves to private IP) but connection fails

**Good news:** Private Link DNS is configured correctly!

**Check these in order:**

1. **Load Balancer Health:**
   - Azure Portal → Your Load Balancer → Backend Pools
   - Are targets "Healthy"?
   - ❌ If unhealthy → Check backend service is running

2. **NSG Rules:**
   ```bash
   az network nsg rule list --nsg-name <your-nsg> --resource-group <rg>
   ```
   - Must allow traffic from Private Endpoint subnet to your service port

3. **Backend Service:**
   ```bash
   ssh user@backend-vm
   sudo netstat -tlnp | grep <your-port>
   ```
   - Service must be running and listening

For more details: [TROUBLESHOOTING_FLOWCHART.md](./TROUBLESHOOTING_FLOWCHART.md) Section C

---

## 📋 Configuration Checklist

Before running tests, verify your configuration:

- [ ] **Domains:** Full FQDN (e.g., `api.internal.contoso.com`)
  - ✅ `api.internal.contoso.com`
  - ❌ `https://api.internal.contoso.com` (no protocol)
  - ❌ `*.internal.contoso.com` (no wildcards)

- [ ] **Private DNS Zone:** Zone suffix only (e.g., `internal.contoso.com`)
  - ✅ `internal.contoso.com`
  - ❌ `api.internal.contoso.com` (no specific hostname)

- [ ] **NCC Domain:** Must match Private DNS Zone exactly
  - ✅ `internal.contoso.com`
  - ❌ `https://internal.contoso.com` (no protocol)
  - ❌ `*.internal.contoso.com` (no wildcards)
  - 🔥 **This is the #1 cause of issues!**

- [ ] **Expected IP Prefix:** First 2 octets of your VNet
  - If VNet is `10.0.0.0/16` → use `"10.0"`
  - If VNet is `172.16.0.0/12` → use `"172.16"`

---

## 🎓 Understanding Your Results

### **What "SUCCESS" Means:**
- ✅ DNS resolves to private IP (not public)
- ✅ Private IP is in your VNet range
- ✅ TCP connection succeeds
- ✅ Connection is reliable
- **→ Private Link is working correctly!**

### **What "PUBLIC IP" Means:**
- ❌ DNS resolves to a public IP address
- ❌ Traffic is going through the internet, not Private Link
- ❌ Your Private Link setup is not working
- **→ Usually NCC Domain ≠ Private DNS Zone name**

### **What "DNS FAILED" Means:**
- ❌ Domain name doesn't resolve at all
- ❌ Either DNS record is missing or domain name is wrong
- **→ Check DNS records and spelling**

### **What "TCP FAILED" Means:**
- ✅ DNS is working (resolves to private IP)
- ❌ But can't connect to the service
- **→ Backend, Load Balancer, or NSG issue**

---

## 📊 Comparison Testing (Optional but Recommended)

For thorough troubleshooting, run tests from **both** environments:

### **1. From Databricks:** (What you want to fix)
Use: `databricks_private_link_diagnostics_enhanced.py`

### **2. From Azure VM:** (Validates Azure infrastructure)
Use: `azure_vm_diagnostics.sh`

### **Compare Results:**

| Databricks | Azure VM | Diagnosis |
|------------|----------|-----------|
| ❌ Public IP | ❌ Public IP | DNS Zone issue |
| ❌ Public IP | ✅ Private IP | **NCC issue** ⭐ |
| ✅ Private IP | ✅ Private IP | Both working or both failing consistently |

This tells you whether the problem is in Azure infrastructure or Databricks NCC configuration.

---

## 💡 Pro Tips

1. **Always wait 5-10 minutes** after making changes (DNS propagation time)

2. **Restart Databricks cluster** after changing NCC configuration

3. **Save JSON output** before and after making changes (for comparison)

4. **Run Azure VM test** if Databricks test fails (helps isolate the issue)

5. **90% of issues** are: Private DNS Zone name ≠ NCC Domain name

6. **Use the result analyzer:**
   ```bash
   python analyze_results.py
   # Then paste your JSON output
   ```

---

## 📞 Need More Help?

### **Still Stuck?**
1. Read [TROUBLESHOOTING_FLOWCHART.md](./TROUBLESHOOTING_FLOWCHART.md)
2. Follow the step-by-step guide for your specific issue
3. Run both Databricks and Azure VM tests

### **Opening a Support Ticket?**
Provide:
- [ ] JSON output from Databricks enhanced test
- [ ] Full output from Azure VM test (if run)
- [ ] Screenshots of NCC configuration
- [ ] Screenshots of Private DNS Zone
- [ ] List of all Azure resource names and IDs

### **Want to Understand More?**
Read [README.md](./README.md) for:
- Complete documentation
- Architecture explanation
- Advanced usage scenarios
- Azure CLI command reference

---

## 🎯 Success Metrics

You'll know everything is configured correctly when:

1. ✅ DNS resolves to **private IP** (not public)
2. ✅ Private IP is in **expected range** (your VNet)
3. ✅ TCP connection **succeeds** on first try
4. ✅ Connection is **reliable** (multiple attempts succeed)
5. ✅ Configuration shows `Private DNS Zone = NCC Domain`

---

## 📚 File Recommendations by Scenario

### **Scenario: First time using this suite**
1. Read: `CHEAT_SHEET.txt` (3 min)
2. Run: `databricks_private_link_diagnostics_enhanced.py`
3. If issues: `TROUBLESHOOTING_FLOWCHART.md`

### **Scenario: Tests are failing**
1. Check: Test output for error type
2. Read: `TROUBLESHOOTING_FLOWCHART.md` → Relevant section
3. Apply: Fixes from the flowchart
4. Re-run: Diagnostic test

### **Scenario: Want complete understanding**
1. Read: `SUMMARY.md` (overview)
2. Read: `README.md` (full docs)
3. Read: `TROUBLESHOOTING_FLOWCHART.md` (all scenarios)
4. Bookmark: `CHEAT_SHEET.txt` (quick reference)

### **Scenario: Need to show someone else**
1. Share: `SUMMARY.md` (explains what this is)
2. Share: `CHEAT_SHEET.txt` (quick start)
3. Share: JSON output from your tests

---

## ✨ What Makes This Suite Powerful

- ✅ **Comprehensive:** Tests DNS, TCP, reliability, latency
- ✅ **Intelligent:** Automatically detects root causes
- ✅ **Actionable:** Provides specific fixes, not just problems
- ✅ **Professional:** Color-coded output, JSON export, detailed metrics
- ✅ **Complete:** Works for both Databricks and Azure VM testing
- ✅ **Well-documented:** 5 guides covering all scenarios

---

## 🚀 Ready to Start?

**Your next action depends on where you are:**

- 🆕 **New user?** → Open `CHEAT_SHEET.txt`
- 🔧 **Ready to test?** → Run `databricks_private_link_diagnostics_enhanced.py`
- 🐛 **Have errors?** → Open `TROUBLESHOOTING_FLOWCHART.md`
- 📖 **Want to learn?** → Read `README.md`
- 🤔 **Not sure?** → Read `SUMMARY.md`

**Remember:** Most issues (90%) are solved by ensuring:
```
Private DNS Zone name = NCC Domain name (EXACTLY!)
```

---

**Good luck! 🎉**

If you get stuck, the troubleshooting flowchart has step-by-step instructions for every scenario.
