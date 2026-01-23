# Azure Private Link Troubleshooting Flowchart

## 🎯 Quick Decision Tree

```
START: Run Databricks Enhanced Diagnostics
    |
    ├─→ DNS Resolution Failed? ─────YES──→ DNS Troubleshooting Path
    |                                      (See Section A)
    |
    ├─→ DNS Resolves to Public IP? ─YES──→ Private Link Not Working
    |                                      (See Section B - MOST COMMON)
    |
    ├─→ DNS Resolves to Private IP? ─YES─→ TCP Connection Failed?
    |                                       |
    |                                       ├─→ YES → Backend/LB Issue
    |                                       |         (See Section C)
    |                                       |
    |                                       └─→ NO → SUCCESS! ✅
    |
    └─→ Inconsistent Results? ──────YES──→ Reliability Issues
                                           (See Section D)
```

---

## Section A: DNS Resolution Failed

### Symptom
```
❌ DNS resolution failed: [Errno -2] Name or service not known
```

### Diagnosis Path

**Step 1: Verify DNS Record Exists**
```bash
az network private-dns record-set a list \
  --zone-name <your-zone> \
  --resource-group <your-rg> \
  --output table
```

**Decision:**
- Record exists → Go to Step 2
- Record missing → **FIX: Create DNS Record**

**FIX: Create DNS Record**
```bash
az network private-dns record-set a add-record \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --record-set-name <hostname> \
  --ipv4-address <lb-private-ip>
```

---

**Step 2: Verify Domain Name Spelling**
- Check for typos in your DOMAINS_TO_TEST configuration
- Ensure domain ends with your DNS zone suffix
- Example: If zone is `internal.contoso.com`
  - ✅ Correct: `api.internal.contoso.com`
  - ❌ Wrong: `api.internal.contos.com` (typo)

---

**Step 3: Verify Private DNS Zone Exists**
```bash
az network private-dns zone show \
  --name <your-zone> \
  --resource-group <your-rg>
```

**Decision:**
- Zone exists → Go to Step 4
- Zone missing → **FIX: Create Private DNS Zone**

---

**Step 4: Verify VNet Link**
```bash
az network private-dns link vnet list \
  --zone-name <your-zone> \
  --resource-group <your-rg> \
  --output table
```

**Check:**
- Is the VNet linked?
- Is the link enabled?
- Is it the correct VNet (where Private Endpoint is)?

**FIX: Create VNet Link**
```bash
az network private-dns link vnet create \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <link-name> \
  --virtual-network <vnet-id> \
  --registration-enabled false
```

---

## Section B: Private Link Not Working (Public IP Resolved) 🔥

### Symptom
```
❌ IP Type: PUBLIC IP - Private Link is NOT being used!
Overall Status: ❌ PRIVATE LINK NOT WORKING
```

### This is the MOST COMMON issue. Follow this path carefully:

---

### Check 1: DNS Zone Name vs NCC Domain ⭐ MOST COMMON FIX

**Verify in Diagnostic Output:**
```
Your Configuration:
  Private DNS Zone:     internal.contoso.com
  NCC Domain:           internal.contoso.com
```

**These MUST match EXACTLY (character for character, case-sensitive)**

| If They Match | If They Don't Match |
|---------------|---------------------|
| ✅ Go to Check 2 | ❌ **THIS IS YOUR PROBLEM** |

**FIX: Update NCC Domain**
1. Go to Databricks Account Console
2. Navigate to Network Connectivity Config
3. Edit the NCC
4. Update Domain to match Private DNS Zone exactly
5. Wait 5-10 minutes for propagation
6. Restart Databricks cluster
7. Re-run diagnostic test

**Common Mistakes:**
```
DNS Zone:  internal.contoso.com
NCC:       contoso.com              ❌ Wrong (missing subdomain)
NCC:       https://internal...      ❌ Wrong (has protocol)
NCC:       *.internal.contoso.com   ❌ Wrong (has wildcard)
NCC:       api.internal.contoso.com ❌ Wrong (specific hostname)
```

---

### Check 2: DNS A Record Points to Correct IP

**Verify A Record:**
```bash
az network private-dns record-set a list \
  --zone-name <your-zone> \
  --resource-group <your-rg> \
  --query "[].{Name:name, IP:aRecords[0].ipv4Address}" \
  --output table
```

**Get Load Balancer Frontend IP:**
```bash
az network lb frontend-ip show \
  --resource-group <your-rg> \
  --lb-name <your-lb> \
  --name <frontend-name> \
  --query privateIPAddress \
  --output tsv
```

**These MUST match!**

**FIX: Update A Record**
```bash
# Remove old record
az network private-dns record-set a remove-record \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --record-set-name <hostname> \
  --ipv4-address <old-ip>

# Add correct record
az network private-dns record-set a add-record \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --record-set-name <hostname> \
  --ipv4-address <correct-lb-ip>
```

---

### Check 3: VNet Link is Active

**Verify VNet Link:**
```bash
az network private-dns link vnet show \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <link-name> \
  --query "{State:provisioningState, VNet:virtualNetwork.id}" \
  --output table
```

**Expected:** State = Succeeded

**FIX: Recreate VNet Link** (if failed)
```bash
# Delete failed link
az network private-dns link vnet delete \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <link-name>

# Create new link
az network private-dns link vnet create \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <link-name> \
  --virtual-network <vnet-id> \
  --registration-enabled false
```

---

### Check 4: Private Endpoint Status

**Verify in Databricks Account Console:**
1. Go to Cloud Resources → Network Connectivity Configs
2. Find your NCC
3. Check Private Endpoint status

**Expected:** Status = "Established"

| Status | Meaning | Action |
|--------|---------|--------|
| Pending | Waiting for approval | Approve in Azure Portal |
| Established | ✅ Working | Continue to Check 5 |
| Rejected | Rejected | Delete and recreate |
| Disconnected | Connection lost | Delete and recreate |

**FIX: Approve Private Endpoint** (if Pending)
```bash
az network private-endpoint-connection approve \
  --resource-group <your-rg> \
  --resource-name <private-link-service-name> \
  --name <pe-connection-name> \
  --type Microsoft.Network/privateLinkServices
```

---

### Check 5: Workspace is Using NCC

**Verify in Databricks Workspace:**
1. Go to Workspace Settings
2. Navigate to Advanced → Network
3. Check if NCC is listed

**If NCC is NOT listed:**
- Workspace may have been created before NCC
- NCC may not be attached

**FIX: Attach NCC to Workspace**
- This typically requires recreating the workspace with NCC attached
- Contact Databricks support for migration options

**Test if NCC is Active (from notebook):**
```python
import requests
egress_ip = requests.get("https://ifconfig.me").text
print(f"Egress IP: {egress_ip}")

# If this is a public Azure IP, NCC is NOT active
```

---

### Check 6: NCC Domain Configuration Format

**In Databricks Account Console → NCC → Domains:**

**CORRECT Format:**
```
internal.contoso.com
```

**INCORRECT Formats:**
```
https://internal.contoso.com       ❌ No protocol
http://internal.contoso.com        ❌ No protocol
*.internal.contoso.com             ❌ No wildcards
api.internal.contoso.com           ❌ No specific hostname
internal.contoso.com/              ❌ No trailing slash
internal.contoso.com:443           ❌ No port
```

**Rule:** Enter ONLY the DNS zone suffix, nothing else.

---

### Summary Checklist for Public IP Issue

Work through this checklist in order:

- [ ] Private DNS Zone name = NCC Domain (exact match)
- [ ] DNS A record points to Load Balancer private IP
- [ ] VNet link is active and points to correct VNet
- [ ] Private Endpoint status is "Established"
- [ ] Workspace is attached to NCC
- [ ] NCC Domain has no protocol/wildcards/hostnames
- [ ] Waited 5-10 minutes after making changes
- [ ] Restarted Databricks cluster
- [ ] Re-ran diagnostic test

**If ALL boxes checked and still failing:**
- Run Azure VM diagnostic script
- Compare results
- Open support ticket with both outputs

---

## Section C: Backend/Load Balancer Issue

### Symptom
```
✅ DNS Resolution: 10.0.1.100 (private IP)
❌ TCP Connection: Connection timeout
```

**Good news:** Private Link DNS is working!
**Issue:** Backend service not reachable

---

### Check 1: Load Balancer Health Probe

**Check Backend Health:**
```bash
az network lb show \
  --name <lb-name> \
  --resource-group <your-rg> \
  --query "backendAddressPools[].backendIPConfigurations[].{IP:privateIPAddress, Health:healthProbeSettings}" \
  --output table
```

**Or check in Azure Portal:**
1. Navigate to Load Balancer
2. Click "Backend pools"
3. Look at health status of targets

**Expected:** All targets show "Healthy"

**If Unhealthy:**
- Backend VM may be down
- Service may not be running on backend
- Health probe port may be wrong

**FIX: Check Backend Service**
```bash
# SSH to backend VM
ssh user@backend-vm

# Check if service is running
sudo netstat -tlnp | grep <port>

# Check if service responds locally
curl -v localhost:<port>

# Check service logs
sudo journalctl -u <service-name> -f
```

---

### Check 2: Backend Pool Configuration

**Verify Backend Pool:**
```bash
az network lb address-pool show \
  --resource-group <your-rg> \
  --lb-name <lb-name> \
  --name <backend-pool-name>
```

**Verify:**
- Pool contains backend VM(s)
- VMs are in correct VNet/subnet
- VM NICs are correctly attached

---

### Check 3: NSG Rules (Private Endpoint Subnet)

**Check NSG on Private Endpoint Subnet:**
```bash
# Get Private Endpoint subnet
az network private-endpoint show \
  --name <pe-name> \
  --resource-group <your-rg> \
  --query "subnet.id" \
  --output tsv

# Check NSG rules
az network nsg rule list \
  --nsg-name <nsg-name> \
  --resource-group <your-rg> \
  --output table
```

**Required Rule:**
- Allow inbound from Private Endpoint subnet to backend port

**FIX: Add NSG Rule**
```bash
az network nsg rule create \
  --resource-group <your-rg> \
  --nsg-name <nsg-name> \
  --name AllowPrivateEndpoint \
  --priority 100 \
  --direction Inbound \
  --source-address-prefixes <private-endpoint-subnet-cidr> \
  --destination-port-ranges <your-port> \
  --protocol Tcp \
  --access Allow
```

---

### Check 4: NSG Rules (Backend VM)

**Check NSG on Backend VM NIC:**
```bash
az network nsg rule list \
  --nsg-name <backend-nsg-name> \
  --resource-group <your-rg> \
  --query "[?direction=='Inbound'].{Name:name, Priority:priority, SourceAddressPrefix:sourceAddressPrefix, DestinationPortRange:destinationPortRange, Access:access}" \
  --output table
```

**Required:**
- Allow inbound from Load Balancer subnet or VNet
- No deny rules blocking traffic

---

### Check 5: Load Balancer Rules

**Verify LB Rules:**
```bash
az network lb rule list \
  --resource-group <your-rg> \
  --lb-name <lb-name> \
  --output table
```

**Verify:**
- Rule exists for your port
- Frontend IP is correct
- Backend pool is correct
- Health probe is attached

---

### Check 6: Service Running on Backend

**Test from Azure VM (in same VNet):**
```bash
# SSH to test VM in same VNet
ssh user@test-vm

# Test connectivity to backend directly
nc -zv <backend-private-ip> <port>

# Test through Load Balancer
nc -zv <lb-private-ip> <port>
```

**If direct to backend works but LB doesn't:**
- Load Balancer misconfiguration

**If direct to backend fails:**
- Backend service issue

---

## Section D: Reliability Issues

### Symptom
```
⚠️  DNS is inconsistent - resolved to 2 different IPs
⚠️  2/5 connections failed
Overall Status: ⚠️  PASS - But connection is unreliable
```

---

### Issue 1: Inconsistent DNS

**Possible Causes:**
- Multiple A records for same hostname
- DNS round-robin
- Caching issues

**FIX: Check for Duplicate Records**
```bash
az network private-dns record-set a show \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <hostname>
```

**If multiple IPs:** Remove duplicates if unintended

---

### Issue 2: Intermittent Connection Failures

**Possible Causes:**
- Backend VM overloaded
- Health probe intermittently failing
- Network congestion
- Backend service crashing

**Diagnostics:**
1. Check backend VM CPU/Memory
2. Check Load Balancer metrics
3. Review backend service logs
4. Monitor health probe status

---

## 🛠️ Emergency Troubleshooting Steps

If all else fails, try these steps in order:

### 1. Restart Everything
```bash
# Restart backend service
sudo systemctl restart <service>

# In Databricks: Restart cluster
# In Azure Portal: Restart backend VM (if necessary)
```

### 2. Recreate DNS Record
```bash
# Delete
az network private-dns record-set a delete \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <hostname>

# Recreate
az network private-dns record-set a create \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <hostname>

az network private-dns record-set a add-record \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --record-set-name <hostname> \
  --ipv4-address <lb-private-ip>
```

### 3. Recreate VNet Link
```bash
# Delete old link
az network private-dns link vnet delete \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <link-name>

# Create new link
az network private-dns link vnet create \
  --resource-group <your-rg> \
  --zone-name <your-zone> \
  --name <link-name> \
  --virtual-network <vnet-id> \
  --registration-enabled false
```

### 4. Update NCC Configuration
1. Go to Databricks Account Console
2. Edit Network Connectivity Config
3. Verify all settings
4. Save (even if no changes)
5. Wait 10 minutes
6. Restart cluster
7. Re-test

---

## 📞 When to Contact Support

Contact support if:

1. ✅ All checklist items verified
2. ✅ Both Databricks and Azure VM tests run
3. ✅ All configurations match exactly
4. ❌ Still not working after 24 hours

**Provide to Support:**
- JSON output from Databricks enhanced diagnostic
- Full output from Azure VM diagnostic
- Screenshots of NCC configuration
- Screenshots of Private DNS Zone configuration
- Azure resource IDs (subscription, RG, resources)

---

## 📊 Quick Reference Table

| Symptom | Root Cause | Section | Urgency |
|---------|-----------|---------|---------|
| DNS fails | Missing record | A | Medium |
| Public IP | NCC misconfigured | B | 🔥 Critical |
| Private IP, TCP fails | Backend/LB issue | C | High |
| Intermittent | Reliability issue | D | Medium |

---

**Last Updated:** 2026-01-23
