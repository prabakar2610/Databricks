# Private Link Validation (Azure VM)

**Azure VM-based Private Link validation script**

## 📋 Overview

This bash script validates Private Link connectivity from an Azure VM in your VNet. It's designed to compare network behavior between Azure VMs and Databricks, helping isolate whether issues are Databricks-specific or general network configuration problems.

**Run Time:** ~2 minutes  
**Environment:** Azure VM (in same VNet as Databricks) or Azure Cloud Shell  
**Requirements:** Azure CLI, bash, network tools (dig, nc, curl)

---

## 🎯 When to Use

Use this script when you need to:

- ✅ Compare VM vs Databricks connectivity
- ✅ Validate VNet infrastructure is working
- ✅ Isolate Databricks-specific vs general network issues
- ✅ Verify Private DNS Zone configuration
- ✅ Test load balancer connectivity from VNet
- ✅ Baseline network behavior before Databricks testing

---

## 🚀 Usage

### **Method 1: Run on Azure VM**

```bash
# SSH into your Azure VM (must be in same VNet as Databricks)
ssh user@your-vm-ip

# Download the script
curl -o private_link_test.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/private_link_validation/script.sh

# Make it executable
chmod +x private_link_test.sh

# Edit configuration
nano private_link_test.sh
# Update DOMAINS_TO_TEST, PRIVATE_DNS_ZONE, etc.

# Run the script
./private_link_test.sh
```

### **Method 2: Run in Azure Cloud Shell**

```bash
# Open Azure Cloud Shell (bash mode)
# Download and run
curl -o test.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/private_link_validation/script.sh
chmod +x test.sh

# Edit configuration
code test.sh  # or vi test.sh

# Run
./test.sh
```

### **Method 3: Clone and Run**

```bash
# Clone repository
git clone https://github.com/prabakar2610/Databricks.git
cd Databricks/network_analysis/azure_cli_scripts/private_link_validation

# Edit configuration
nano script.sh

# Run
./script.sh
```

---

## ⚙️ Configuration

### **Edit the Configuration Section**

Open `script.sh` and modify these variables:

```bash
# Domains/endpoints to test
DOMAINS_TO_TEST=(
    "api.yourdomain.com:443:API Service HTTPS"
    "db.yourdomain.com:5432:PostgreSQL Database"
)

# Your Private DNS Zone name
PRIVATE_DNS_ZONE="yourdomain.com"

# Expected private IP prefix
EXPECTED_PRIVATE_IP_PREFIX="10.0"

# Expected Load Balancer IP (optional)
EXPECTED_LB_IP="10.0.1.100"
```

### **Configuration Parameters**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `DOMAINS_TO_TEST` | Array of domains to test | `"api.example.com:443:API"` |
| `PRIVATE_DNS_ZONE` | Private DNS Zone name | `"internal.example.com"` |
| `EXPECTED_PRIVATE_IP_PREFIX` | First 2 octets of private IP | `"10.0"` or `"172.16"` |
| `EXPECTED_LB_IP` | Load balancer frontend IP | `"10.0.1.100"` (optional) |

---

## 📊 What It Tests

### **1. DNS Resolution**
- 🔍 Resolves domains using system DNS
- 🔍 Validates private vs public IP
- 🔍 Checks DNS server configuration
- 🔍 Uses `dig` for detailed DNS analysis

### **2. TCP Connectivity**
- 🔌 Tests TCP connection with `nc` (netcat)
- 🔌 Validates port accessibility
- 🔌 Connection timeout detection
- 🔌 Port open/closed status

### **3. HTTP/HTTPS Connectivity**
- 🌐 Tests HTTP GET requests with `curl`
- 🌐 Validates certificate (HTTPS)
- 🌐 Response code analysis
- 🌐 Connection time measurement

### **4. Network Interface Info**
- 📡 Lists network interfaces
- 📡 Shows IP addresses
- 📡 Displays routing table
- 📡 DNS server configuration

### **5. NSG Validation** (if Azure CLI available)
- 🛡️ Lists NSG rules
- 🛡️ Checks for blocking rules
- 🛡️ Validates allow rules
- 🛡️ Identifies missing rules

---

## 📤 Output

### **Console Output**

```
==================================================
Azure VM Private Link Validation Script
==================================================

Configuration:
  Private DNS Zone: yourdomain.com
  Expected IP Prefix: 10.0.x.x
  Domains to test: 2

==================================================
DNS Resolution Tests
==================================================

Testing: api.yourdomain.com

✓ DNS Resolution: SUCCESS
  IP Address: 10.0.1.100
  ✓ Resolves to PRIVATE IP (expected)

==================================================
TCP Connectivity Tests
==================================================

Testing: api.yourdomain.com:443

✓ TCP Connection: SUCCESS
  Target: 10.0.1.100:443
  Status: CONNECTED

==================================================
HTTP/HTTPS Tests
==================================================

Testing: https://api.yourdomain.com

✓ HTTP Request: SUCCESS
  Status Code: 200
  Response Time: 0.234s

==================================================
Summary
==================================================

✓ All tests PASSED

DNS Resolution: 2/2 (100%)
TCP Connectivity: 2/2 (100%)
HTTP Requests: 2/2 (100%)

Private IP Detection: 2/2 (100%)
```

---

## 🆘 Troubleshooting Common Issues

### **Issue 1: Script Not Found**

**Symptom:**
```
bash: ./script.sh: No such file or directory
```

**Solution:**
- Check current directory: `pwd`
- List files: `ls -la`
- Navigate to correct directory
- Verify file was downloaded

---

### **Issue 2: Permission Denied**

**Symptom:**
```
bash: ./script.sh: Permission denied
```

**Solution:**
```bash
chmod +x script.sh
./script.sh
```

---

### **Issue 3: Command Not Found (dig, nc, curl)**

**Symptom:**
```
dig: command not found
nc: command not found
```

**Solution Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y dnsutils netcat curl
```

**Solution RHEL/CentOS:**
```bash
sudo yum install -y bind-utils nmap-ncat curl
```

---

### **Issue 4: DNS Resolves to Public IP from VM**

**Symptom:**
```
✗ DNS Resolution
  IP Address: 20.123.45.67
  ✗ Resolves to PUBLIC IP (private expected)
```

**Possible Causes:**
1. VM not using Azure DNS (168.63.129.16)
2. Private DNS Zone not linked to VM's VNet
3. Custom DNS server not configured for Private DNS
4. Domain not registered in Private DNS Zone

**Solutions:**
- Check VM DNS settings: `cat /etc/resolv.conf`
- Verify DNS server is 168.63.129.16 (Azure DNS)
- Link Private DNS Zone to VNet in Azure Portal
- Add A record for domain in Private DNS Zone
- If using custom DNS, configure conditional forwarding to 168.63.129.16

---

### **Issue 5: TCP Connection Fails from VM**

**Symptom:**
```
✗ TCP Connection: FAILED
  Error: Connection timed out
```

**Possible Causes:**
1. NSG blocking traffic
2. Load balancer not configured
3. Backend service not running
4. UDR routing traffic incorrectly

**Solutions:**
- Check NSG rules: `./script.sh` (NSG validation section)
- Verify load balancer backend pool health
- Check backend service status
- Review route table (UDR)
- Test from same subnet as Databricks

---

### **Issue 6: Works from VM but Not from Databricks**

**This is the key scenario this script helps identify!**

**If VM test passes but Databricks fails:**

**Possible Databricks-specific causes:**
1. Databricks VNet integration not configured
2. NCC (Network Connectivity Config) not configured (serverless)
3. Databricks NSG rules blocking traffic
4. Different subnet with different NSG/UDR
5. Databricks-specific firewall rules

**Solutions:**
- For classic compute: Check Databricks subnet NSG
- For serverless: Configure NCC with Private Link
- Verify Databricks VNet injection configuration
- Check if Databricks subnet has different UDR
- Review Databricks IP access lists

---

## 📖 VM Setup Requirements

### **Recommended VM Configuration**

**VM Requirements:**
- ✅ Same VNet as Databricks
- ✅ Preferably same subnet or peered subnet
- ✅ Azure DNS (168.63.129.16)
- ✅ Network tools installed (dig, nc, curl)
- ✅ Azure CLI (optional, for NSG validation)

### **Create Test VM (Azure CLI)**

```bash
# Variables
RG="your-resource-group"
VNET="your-vnet-name"
SUBNET="your-subnet-name"
VM_NAME="private-link-test-vm"

# Create VM
az vm create \
  --resource-group $RG \
  --name $VM_NAME \
  --vnet-name $VNET \
  --subnet $SUBNET \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys

# Get VM IP
az vm list-ip-addresses -g $RG -n $VM_NAME --output table

# SSH to VM
ssh azureuser@<VM-IP>

# Install tools
sudo apt-get update
sudo apt-get install -y dnsutils netcat curl

# Install Azure CLI (optional)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

---

## 💡 Tips

1. **Use same VNet as Databricks** - Most accurate comparison
2. **Use same subnet if possible** - Identical NSG/UDR configuration
3. **Save script output** - Compare with Databricks results
4. **Test before Databricks** - Validates infrastructure first
5. **Run on VM in VNet** - Cloud Shell may not have VNet access
6. **Check DNS server** - Must be Azure DNS (168.63.129.16)
7. **Compare outputs** - Key to isolating Databricks-specific issues

---

## 🔍 Comparing VM vs Databricks Results

### **Scenario 1: Both Pass**
✅ **Infrastructure OK** - Issue likely not network-related

### **Scenario 2: Both Fail**
❌ **Infrastructure Issue** - Fix VNet/DNS/Load Balancer configuration

### **Scenario 3: VM Passes, Databricks Fails**
⚠️ **Databricks Configuration Issue** - Check:
- Databricks VNet injection
- NCC configuration (serverless)
- Databricks-specific NSG rules
- Subnet differences

### **Scenario 4: VM Fails, Databricks Passes**
🤔 **Unusual** - Check:
- VM DNS configuration
- VM subnet NSG
- VM in different VNet?

---

## 📖 Related Documentation

- [Azure Private Link](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview)
- [Azure Private DNS](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
- [Azure Load Balancer](https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-overview)
- [Network Security Groups](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)

---

## 🔗 Quick Links

- **Main Repository**: https://github.com/prabakar2610/Databricks
- **All Network Scripts**: [../../](../../)
- **Databricks Private Link Test**: [../../databricks_notebooks/private_link_diagnostics/](../../databricks_notebooks/private_link_diagnostics/)
- **Classic Compute Validation**: [../classic_compute_validation/](../classic_compute_validation/)

---

**Version:** 3.0  
**Last Updated:** 2026-01-24  
**Script:** `script.sh`  
**Platform:** Linux/bash
