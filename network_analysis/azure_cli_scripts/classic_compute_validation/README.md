# Classic Compute VNet/NSG Validation

**VNet injection and NSG validation for Azure Databricks Classic Compute**

## 📋 Overview

This Azure CLI script validates VNet injection configuration and Network Security Group (NSG) rules for Azure Databricks classic compute clusters. It ensures your VNet is properly configured for Databricks and identifies common configuration issues.

**Run Time:** ~1 minute  
**Environment:** Terminal with Azure CLI  
**Requirements:** Azure CLI, bash, sufficient Azure permissions

---

## 🎯 When to Use

Use this script when you:

- ✅ Setting up new Databricks workspace with VNet injection
- ✅ Troubleshooting classic compute cluster launch failures
- ✅ Validating NSG rules for Databricks subnets
- ✅ Checking subnet delegation
- ✅ Verifying VNet configuration
- ✅ Diagnosing networking issues with classic clusters
- ✅ Auditing Databricks network security

---

## 🚀 Usage

### **Method 1: Run Directly**

```bash
# Download the script
curl -o databricks_vnet_check.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/classic_compute_validation/script.sh

# Make executable
chmod +x databricks_vnet_check.sh

# Run with your configuration
./databricks_vnet_check.sh \
  --resource-group "your-rg" \
  --vnet-name "your-vnet" \
  --public-subnet "public-subnet" \
  --private-subnet "private-subnet"
```

### **Method 2: Interactive Mode**

```bash
# Download and run
curl -o check.sh https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/azure_cli_scripts/classic_compute_validation/script.sh
chmod +x check.sh

# Edit configuration section
nano check.sh

# Run
./check.sh
```

### **Method 3: Clone and Run**

```bash
# Clone repository
git clone https://github.com/prabakar2610/Databricks.git
cd Databricks/network_analysis/azure_cli_scripts/classic_compute_validation

# Edit configuration
nano script.sh

# Run
./script.sh
```

---

## ⚙️ Configuration

### **Command Line Arguments**

```bash
./script.sh \
  --resource-group "my-databricks-rg" \
  --vnet-name "databricks-vnet" \
  --public-subnet "public-subnet" \
  --private-subnet "private-subnet" \
  --workspace-name "my-databricks-ws"  # Optional
```

### **Or Edit Configuration in Script**

```bash
# Configuration section
RESOURCE_GROUP="your-resource-group"
VNET_NAME="your-vnet-name"
PUBLIC_SUBNET="databricks-public"
PRIVATE_SUBNET="databricks-private"
WORKSPACE_NAME="your-workspace-name"  # Optional
```

### **Configuration Parameters**

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `RESOURCE_GROUP` | Yes | Resource group containing VNet | `"databricks-rg"` |
| `VNET_NAME` | Yes | Virtual Network name | `"databricks-vnet"` |
| `PUBLIC_SUBNET` | Yes | Public (host) subnet name | `"public-subnet"` |
| `PRIVATE_SUBNET` | Yes | Private (container) subnet name | `"private-subnet"` |
| `WORKSPACE_NAME` | No | Databricks workspace name | `"my-workspace"` |

---

## 📊 What It Tests

### **1. Azure CLI & Authentication**
- ✅ Azure CLI installed
- ✅ Logged in to Azure
- ✅ Correct subscription selected

### **2. Resource Group & VNet**
- ✅ Resource group exists
- ✅ VNet exists in resource group
- ✅ VNet configuration details

### **3. Subnet Configuration**
- ✅ Public subnet exists
- ✅ Private subnet exists
- ✅ Subnet address prefixes
- ✅ Subnet delegation to Databricks
- ✅ Subnet size (minimum /26 recommended)

### **4. NSG Rules Validation**
- ✅ NSGs attached to subnets
- ✅ Required inbound rules
- ✅ Required outbound rules
- ✅ Rule priorities
- ✅ Service tags usage
- ✅ Identifies missing or incorrect rules

### **5. Databricks-Specific Requirements**
- ✅ Subnet delegation to `Microsoft.Databricks/workspaces`
- ✅ Control plane connectivity rules
- ✅ Worker node communication rules
- ✅ Storage account access rules
- ✅ Metastore connectivity rules

---

## 📤 Output

### **Console Output**

```
==================================================
Databricks VNet & NSG Validation Script
==================================================

Configuration:
  Resource Group: databricks-rg
  VNet: databricks-vnet
  Public Subnet: public-subnet
  Private Subnet: private-subnet

==================================================
Validating Azure CLI
==================================================

✓ Azure CLI installed (version 2.50.0)
✓ Logged in as: user@domain.com
✓ Using subscription: Production (xxx-xxx-xxx)

==================================================
Validating Resource Group & VNet
==================================================

✓ Resource group exists: databricks-rg
✓ VNet exists: databricks-vnet
  Location: eastus
  Address Space: 10.0.0.0/16

==================================================
Validating Subnets
==================================================

Public Subnet (public-subnet):
✓ Subnet exists
✓ Address Prefix: 10.0.1.0/24 (/24 - OK)
✓ Delegated to: Microsoft.Databricks/workspaces
✓ NSG attached: databricks-public-nsg

Private Subnet (private-subnet):
✓ Subnet exists
✓ Address Prefix: 10.0.2.0/24 (/24 - OK)
✓ Delegated to: Microsoft.Databricks/workspaces
✓ NSG attached: databricks-private-nsg

==================================================
Validating NSG Rules - Public Subnet
==================================================

Inbound Rules:
✓ Allow AzureDatabricks inbound (priority 100)
✓ Allow internal VNet (priority 200)

Outbound Rules:
✓ Allow AzureDatabricks outbound (priority 100)
✓ Allow SQL (priority 200)
✓ Allow Storage (priority 300)
✓ Allow EventHub (priority 400)

==================================================
Summary
==================================================

✓ ALL VALIDATION CHECKS PASSED

VNet Configuration: OK
Subnet Configuration: OK
Subnet Delegation: OK
NSG Rules: OK

Your Databricks VNet is properly configured!
```

---

## 🆘 Troubleshooting Common Issues

### **Issue 1: Azure CLI Not Logged In**

**Symptom:**
```
✗ ERROR: Please run 'az login' first
```

**Solution:**
```bash
az login

# If multiple subscriptions
az account list --output table
az account set --subscription "your-subscription-name-or-id"
```

---

### **Issue 2: Subnet Not Delegated**

**Symptom:**
```
✗ Subnet NOT delegated to Microsoft.Databricks/workspaces
```

**Impact:** Cluster creation will fail

**Solution:**
```bash
az network vnet subnet update \
  --resource-group databricks-rg \
  --vnet-name databricks-vnet \
  --name public-subnet \
  --delegations Microsoft.Databricks/workspaces

az network vnet subnet update \
  --resource-group databricks-rg \
  --vnet-name databricks-vnet \
  --name private-subnet \
  --delegations Microsoft.Databricks/workspaces
```

---

### **Issue 3: Subnet Too Small**

**Symptom:**
```
⚠ WARNING: Subnet size /28 - Consider /26 or larger for production
```

**Impact:** Limited number of cluster nodes

**Minimum Sizes:**
- Development: /28 (11 usable IPs)
- Production: /26 (59 usable IPs)
- Large: /24 (251 usable IPs)

**Solution:**
If subnet is too small, you'll need to:
1. Create new subnets with larger CIDR
2. Migrate to new subnets (requires workspace recreation)

---

### **Issue 4: Missing NSG Rules**

**Symptom:**
```
✗ Missing required outbound rule: AzureDatabricks
```

**Impact:** Cluster launch failures, control plane connectivity issues

**Solution:**

**Required Outbound Rules:**
```bash
# Allow Databricks control plane
az network nsg rule create \
  --resource-group databricks-rg \
  --nsg-name databricks-public-nsg \
  --name AllowDatabricksControlPlane \
  --priority 100 \
  --direction Outbound \
  --access Allow \
  --protocol Tcp \
  --destination-address-prefixes AzureDatabricks \
  --destination-port-ranges 443

# Allow SQL
az network nsg rule create \
  --resource-group databricks-rg \
  --nsg-name databricks-public-nsg \
  --name AllowSql \
  --priority 200 \
  --direction Outbound \
  --access Allow \
  --protocol Tcp \
  --destination-address-prefixes Sql \
  --destination-port-ranges 3306

# Allow Storage
az network nsg rule create \
  --resource-group databricks-rg \
  --nsg-name databricks-public-nsg \
  --name AllowStorage \
  --priority 300 \
  --direction Outbound \
  --access Allow \
  --protocol Tcp \
  --destination-address-prefixes Storage \
  --destination-port-ranges 443

# Allow Event Hub
az network nsg rule create \
  --resource-group databricks-rg \
  --nsg-name databricks-public-nsg \
  --name AllowEventHub \
  --priority 400 \
  --direction Outbound \
  --access Allow \
  --protocol Tcp \
  --destination-address-prefixes EventHub \
  --destination-port-ranges 9093
```

**Required Inbound Rules:**
```bash
# Allow internal VNet communication
az network nsg rule create \
  --resource-group databricks-rg \
  --nsg-name databricks-public-nsg \
  --name AllowVnetInbound \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol "*" \
  --source-address-prefixes VirtualNetwork \
  --destination-address-prefixes VirtualNetwork \
  --source-port-ranges "*" \
  --destination-port-ranges "*"
```

---

### **Issue 5: No NSG Attached**

**Symptom:**
```
✗ No NSG attached to subnet
```

**Impact:** No network security, or potential misconfiguration

**Solution:**
```bash
# Create NSG
az network nsg create \
  --resource-group databricks-rg \
  --name databricks-public-nsg \
  --location eastus

# Attach to subnet
az network vnet subnet update \
  --resource-group databricks-rg \
  --vnet-name databricks-vnet \
  --name public-subnet \
  --network-security-group databricks-public-nsg

# Add required rules (see Issue 4)
```

---

## 📖 NSG Rules Reference

### **Public Subnet NSG Rules**

#### **Inbound Rules**

| Priority | Name | Source | Destination | Port | Protocol |
|----------|------|--------|-------------|------|----------|
| 100 | AllowVnetInbound | VirtualNetwork | VirtualNetwork | * | * |

#### **Outbound Rules**

| Priority | Name | Destination | Port | Protocol |
|----------|------|-------------|------|----------|
| 100 | AllowDatabricks | AzureDatabricks | 443 | TCP |
| 200 | AllowSql | Sql | 3306 | TCP |
| 300 | AllowStorage | Storage | 443 | TCP |
| 400 | AllowEventHub | EventHub | 9093 | TCP |

### **Private Subnet NSG Rules**

Same as public subnet (both subnets need same rules).

---

## 💡 Tips

1. **Run before workspace creation** - Validate infrastructure first
2. **Use service tags** - Simplifies NSG rule management
3. **Document changes** - Keep track of NSG rule modifications
4. **Test after changes** - Run script after NSG updates
5. **Save output** - Keep for compliance and troubleshooting
6. **Use /26 subnets** - Minimum recommended for production
7. **Separate NSGs** - Use different NSGs for public/private subnets

---

## 🔍 Understanding Databricks Subnets

### **Public Subnet (Host Subnet)**
- Contains cluster management infrastructure
- Needs outbound internet access
- Control plane communication
- Requires delegation to Databricks

### **Private Subnet (Container Subnet)**
- Contains cluster worker nodes
- Executor containers run here
- Needs same NSG rules as public subnet
- Requires delegation to Databricks

### **Subnet Sizing**

| Use Case | Recommended Size | Usable IPs | Max Nodes |
|----------|------------------|------------|-----------|
| Dev/Test | /26 | 59 | ~25 |
| Production | /24 | 251 | ~100 |
| Large-Scale | /22 | 1019 | ~400 |

---

## 📖 Related Documentation

- [Databricks VNet Injection](https://learn.microsoft.com/en-us/azure/databricks/security/network/classic/vnet-inject)
- [Databricks NSG Requirements](https://learn.microsoft.com/en-us/azure/databricks/security/network/classic/security-group-rules)
- [Azure NSG Overview](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)
- [Azure Service Tags](https://learn.microsoft.com/en-us/azure/virtual-network/service-tags-overview)

---

## 🔗 Quick Links

- **Main Repository**: https://github.com/prabakar2610/Databricks
- **All Network Scripts**: [../../](../../)
- **Private Link Validation**: [../private_link_validation/](../private_link_validation/)
- **DNS Diagnostics**: [../../databricks_notebooks/dns_diagnostics/](../../databricks_notebooks/dns_diagnostics/)

---

**Version:** 3.0  
**Last Updated:** 2026-01-24  
**Script:** `script.sh`  
**Platform:** Azure CLI / bash
