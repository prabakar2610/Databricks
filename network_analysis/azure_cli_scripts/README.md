# Azure CLI Scripts - Network Diagnostics

This folder contains Azure CLI scripts for diagnosing Azure Databricks networking from **Azure perspective** (infrastructure validation).

## 📋 Available Scripts

### 1. **01_private_link_validation.sh**
**Validate Private Link setup from Azure VM**

**Use Case:** Compare connectivity from Azure VM vs Databricks to isolate issues

**Tests:**
- DNS resolution with multiple tools (dig, nslookup, host)
- TCP connectivity
- Azure metadata inspection
- Traceroute (optional)
- Port scanning (optional)

**Run On:** Azure VM in same VNet as Private Endpoint

**Time:** ~1-2 minutes

---

### 2. **02_classic_compute_vnet_nsg.sh** ⭐
**Validate VNet injection configuration**

**Use Case:** Verify VNet injection, NSG rules, and UDR configuration

**Tests:**
- Workspace VNet injection status
- VNet and subnet configuration
- Subnet delegations
- NSG rules validation
- Route table configuration

**Run On:** Any machine with Azure CLI (local or Cloud Shell)

**Time:** ~1 minute

**Prerequisites:**
- Azure CLI logged in
- Read permissions on network resources

---

## 🚀 How to Use

### **Setup**

1. Install Azure CLI:
```bash
# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows
# Download from https://aka.ms/installazurecliwindows
```

2. Login:
```bash
az login
az account set --subscription "your-subscription-id"
```

3. Make scripts executable:
```bash
chmod +x *.sh
```

### **Running Scripts**

```bash
# Edit configuration in script
nano 02_classic_compute_vnet_nsg.sh

# Run
./02_classic_compute_vnet_nsg.sh
```

---

## 📊 When to Use Each Script

| Scenario | Use This Script |
|----------|----------------|
| Compare Databricks vs Azure VM connectivity | `01_private_link_validation.sh` |
| Validate VNet injection setup | `02_classic_compute_vnet_nsg.sh` |
| Check NSG rules | `02_classic_compute_vnet_nsg.sh` |
| Verify subnet delegations | `02_classic_compute_vnet_nsg.sh` |
| Validate UDR configuration | `02_classic_compute_vnet_nsg.sh` |

---

## 🎯 Script Comparison

| Feature | Private Link Validation | VNet/NSG Validation |
|---------|------------------------|---------------------|
| DNS Testing | ✅ Multi-tool | ❌ |
| TCP Testing | ✅ | ❌ |
| VNet Configuration | ❌ | ✅ |
| NSG Rules | ❌ | ✅ |
| Subnet Delegation | ❌ | ✅ |
| Route Tables | ❌ | ✅ |
| Requires Azure VM | ✅ | ❌ |
| Requires Azure CLI | ❌ | ✅ |

---

## ⚙️ Configuration

### **Private Link Validation Script**

```bash
# In 01_private_link_validation.sh

DOMAINS_TO_TEST=(
    "api.yourdomain.com:443"
    "database.yourdomain.com:1433"
)

PRIVATE_DNS_ZONE="yourdomain.com"
EXPECTED_LB_IP="10.0.1.100"
EXPECTED_IP_PREFIX="10.0"
```

### **VNet/NSG Validation Script**

```bash
# In 02_classic_compute_vnet_nsg.sh

SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="your-rg"
WORKSPACE_NAME="your-workspace"

VNET_RESOURCE_GROUP="your-vnet-rg"
VNET_NAME="your-vnet"
PUBLIC_SUBNET_NAME="public-subnet"
PRIVATE_SUBNET_NAME="private-subnet"

VNET_INJECTED=true  # Set to false if standard deployment
```

---

## 🔍 What Each Script Validates

### **Private Link Validation (01)**

✅ DNS resolution consistency  
✅ Public vs Private IP  
✅ TCP connectivity  
✅ Network path (traceroute)  
✅ Port accessibility  
✅ Azure VM metadata  

**Output:** Comparison data to identify if issue is Azure infrastructure or Databricks configuration

### **VNet/NSG Validation (02)**

✅ Workspace VNet injection status  
✅ VNet address spaces  
✅ Subnet configurations  
✅ Subnet delegations  
✅ NSG existence and rules  
✅ Inbound/Outbound rules  
✅ Route table configuration  

**Output:** Complete infrastructure validation report

---

## 💡 Best Practices

1. **Run Private Link validation from Azure VM** in same VNet as your resources
2. **Compare results** between Azure VM and Databricks tests
3. **Save outputs** to files for comparison:
   ```bash
   ./02_classic_compute_vnet_nsg.sh > vnet_validation_$(date +%Y%m%d).txt
   ```
4. **Check permissions** before running (need read access to network resources)
5. **Use Cloud Shell** if you don't have Azure CLI locally

---

## 🆘 Troubleshooting

**"az: command not found"**
- Azure CLI not installed
- Install following setup instructions above

**"Authorization failed"**
- Not logged in: `az login`
- Wrong subscription: `az account set --subscription "your-sub-id"`
- Insufficient permissions: Need Network Contributor or Reader role

**"Resource not found"**
- Check resource names in configuration
- Verify subscription and resource group
- Check if resources exist: `az resource list --resource-group your-rg`

**NSG rules not showing**
- NSG might not be attached to subnet
- Check NSG exists: `az network nsg list --output table`

---

## 📖 Required Permissions

**Minimum Azure RBAC roles:**
- **Network Contributor** (preferred) - full network resource access
- **Reader** (minimum) - read-only network resource access

**Specific permissions needed:**
- `Microsoft.Network/*/read`
- `Microsoft.Databricks/workspaces/read`

---

## 🔗 Related Azure CLI Commands

```bash
# List workspaces
az databricks workspace list --output table

# Get workspace details
az databricks workspace show --name <workspace> --resource-group <rg>

# List NSGs
az network nsg list --output table

# List VNets
az network vnet list --output table

# List subnets
az network vnet subnet list --vnet-name <vnet> --resource-group <rg>

# Show route table
az network route-table show --name <route-table> --resource-group <rg>
```

---

## 📚 Reference Documentation

- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)
- [Azure Databricks VNet Injection](https://learn.microsoft.com/en-us/azure/databricks/security/network/classic/vnet-inject)
- [Azure NSG Documentation](https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview)

---

**All scripts provide detailed output** with color-coded success/failure indicators!
