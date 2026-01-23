#!/bin/bash

################################################################################
# Azure Databricks - Classic Compute VNet & NSG Diagnostics
################################################################################
#
# This script validates VNet injection configuration and NSG rules
# for Azure Databricks classic compute plane.
#
# Prerequisites:
#   - Azure CLI installed and logged in
#   - Appropriate permissions to read network resources
#
# Usage:
#   ./02_classic_compute_vnet_nsg.sh
#
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

################################################################################
# CONFIGURATION
################################################################################

# Workspace information
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="your-rg"
WORKSPACE_NAME="your-workspace"

# VNet information (if using VNet injection)
VNET_RESOURCE_GROUP="your-vnet-rg"
VNET_NAME="your-vnet"
PUBLIC_SUBNET_NAME="public-subnet"
PRIVATE_SUBNET_NAME="private-subnet"

# Set to true if using VNet injection
VNET_INJECTED=false

################################################################################
# FUNCTIONS
################################################################################

print_header() {
    echo -e "\n${CYAN}${BOLD}================================================================================"
    echo -e " $1"
    echo -e "================================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

################################################################################
# MAIN SCRIPT
################################################################################

echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║  Azure Databricks - Classic Compute VNet & NSG Diagnostics              ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Set subscription
print_info "Setting subscription: $SUBSCRIPTION_ID"
az account set --subscription "$SUBSCRIPTION_ID"

if [ $? -eq 0 ]; then
    print_success "Subscription set"
else
    print_error "Failed to set subscription"
    exit 1
fi

# Get workspace information
print_header "Workspace Information"

WORKSPACE_INFO=$(az databricks workspace show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$WORKSPACE_NAME" \
    --output json 2>/dev/null)

if [ $? -eq 0 ]; then
    print_success "Workspace found: $WORKSPACE_NAME"
    
    WORKSPACE_ID=$(echo "$WORKSPACE_INFO" | jq -r '.id')
    WORKSPACE_LOCATION=$(echo "$WORKSPACE_INFO" | jq -r '.location')
    WORKSPACE_SKU=$(echo "$WORKSPACE_INFO" | jq -r '.sku.name')
    
    echo "  Resource ID: $WORKSPACE_ID"
    echo "  Location: $WORKSPACE_LOCATION"
    echo "  SKU: $WORKSPACE_SKU"
    
    # Check for VNet injection
    CUSTOM_VNET=$(echo "$WORKSPACE_INFO" | jq -r '.parameters.customVirtualNetworkId.value // empty')
    
    if [ -n "$CUSTOM_VNET" ]; then
        print_success "VNet injection detected"
        VNET_INJECTED=true
        echo "  VNet ID: $CUSTOM_VNET"
    else
        print_info "Standard deployment (no VNet injection)"
        VNET_INJECTED=false
    fi
else
    print_error "Could not retrieve workspace information"
    exit 1
fi

# VNet and NSG diagnostics (only if VNet injected)
if [ "$VNET_INJECTED" = true ]; then
    
    print_header "VNet Configuration"
    
    # Get VNet details
    VNET_INFO=$(az network vnet show \
        --resource-group "$VNET_RESOURCE_GROUP" \
        --name "$VNET_NAME" \
        --output json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        print_success "VNet found: $VNET_NAME"
        
        VNET_ADDRESS_SPACE=$(echo "$VNET_INFO" | jq -r '.addressSpace.addressPrefixes[]' | tr '\n' ' ')
        echo "  Address space: $VNET_ADDRESS_SPACE"
        
        # List subnets
        echo -e "\n  ${BOLD}Subnets:${NC}"
        echo "$VNET_INFO" | jq -r '.subnets[] | "    • \(.name): \(.addressPrefix)"'
    else
        print_error "Could not retrieve VNet information"
    fi
    
    # Check public subnet
    print_header "Public Subnet Configuration"
    
    PUBLIC_SUBNET_INFO=$(az network vnet subnet show \
        --resource-group "$VNET_RESOURCE_GROUP" \
        --vnet-name "$VNET_NAME" \
        --name "$PUBLIC_SUBNET_NAME" \
        --output json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        print_success "Public subnet found: $PUBLIC_SUBNET_NAME"
        
        PUBLIC_ADDRESS_PREFIX=$(echo "$PUBLIC_SUBNET_INFO" | jq -r '.addressPrefix')
        PUBLIC_NSG_ID=$(echo "$PUBLIC_SUBNET_INFO" | jq -r '.networkSecurityGroup.id // "none"')
        PUBLIC_DELEGATION=$(echo "$PUBLIC_SUBNET_INFO" | jq -r '.delegations[0].serviceName // "none"')
        
        echo "  Address prefix: $PUBLIC_ADDRESS_PREFIX"
        echo "  NSG: $(basename $PUBLIC_NSG_ID)"
        echo "  Delegation: $PUBLIC_DELEGATION"
        
        # Check delegation
        if [[ "$PUBLIC_DELEGATION" == *"Microsoft.Databricks"* ]]; then
            print_success "Subnet properly delegated to Databricks"
        else
            print_error "Subnet not delegated to Databricks!"
        fi
        
        # Check NSG
        if [ "$PUBLIC_NSG_ID" != "none" ]; then
            PUBLIC_NSG_NAME=$(basename $PUBLIC_NSG_ID)
            PUBLIC_NSG_RG=$(echo $PUBLIC_NSG_ID | cut -d'/' -f5)
            
            print_info "Checking NSG rules for public subnet..."
            
            az network nsg show \
                --resource-group "$PUBLIC_NSG_RG" \
                --name "$PUBLIC_NSG_NAME" \
                --output table
            
            echo -e "\n  ${BOLD}Inbound Rules:${NC}"
            az network nsg rule list \
                --resource-group "$PUBLIC_NSG_RG" \
                --nsg-name "$PUBLIC_NSG_NAME" \
                --query "[?direction=='Inbound'].{Priority:priority, Name:name, Source:sourceAddressPrefix, Dest:destinationAddressPrefix, Port:destinationPortRange, Action:access}" \
                --output table
            
            echo -e "\n  ${BOLD}Outbound Rules:${NC}"
            az network nsg rule list \
                --resource-group "$PUBLIC_NSG_RG" \
                --nsg-name "$PUBLIC_NSG_NAME" \
                --query "[?direction=='Outbound'].{Priority:priority, Name:name, Source:sourceAddressPrefix, Dest:destinationAddressPrefix, Port:destinationPortRange, Action:access}" \
                --output table
            
            # Check for required rules
            print_info "\nValidating required NSG rules..."
            
            INBOUND_RULES=$(az network nsg rule list \
                --resource-group "$PUBLIC_NSG_RG" \
                --nsg-name "$PUBLIC_NSG_NAME" \
                --query "[?direction=='Inbound']" \
                --output json)
            
            # Check for AzureDatabricks allow rule
            DATABRICKS_ALLOW=$(echo "$INBOUND_RULES" | jq -r '.[] | select(.sourceAddressPrefix | contains("AzureDatabricks")) | .name')
            
            if [ -n "$DATABRICKS_ALLOW" ]; then
                print_success "AzureDatabricks inbound rule found: $DATABRICKS_ALLOW"
            else
                print_warning "No specific AzureDatabricks inbound rule found"
            fi
            
        else
            print_warning "No NSG attached to public subnet"
        fi
    else
        print_error "Could not retrieve public subnet information"
    fi
    
    # Check private subnet
    print_header "Private Subnet Configuration"
    
    PRIVATE_SUBNET_INFO=$(az network vnet subnet show \
        --resource-group "$VNET_RESOURCE_GROUP" \
        --vnet-name "$VNET_NAME" \
        --name "$PRIVATE_SUBNET_NAME" \
        --output json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        print_success "Private subnet found: $PRIVATE_SUBNET_NAME"
        
        PRIVATE_ADDRESS_PREFIX=$(echo "$PRIVATE_SUBNET_INFO" | jq -r '.addressPrefix')
        PRIVATE_NSG_ID=$(echo "$PRIVATE_SUBNET_INFO" | jq -r '.networkSecurityGroup.id // "none"')
        PRIVATE_DELEGATION=$(echo "$PRIVATE_SUBNET_INFO" | jq -r '.delegations[0].serviceName // "none"')
        
        echo "  Address prefix: $PRIVATE_ADDRESS_PREFIX"
        echo "  NSG: $(basename $PRIVATE_NSG_ID)"
        echo "  Delegation: $PRIVATE_DELEGATION"
        
        # Check delegation
        if [[ "$PRIVATE_DELEGATION" == *"Microsoft.Databricks"* ]]; then
            print_success "Subnet properly delegated to Databricks"
        else
            print_error "Subnet not delegated to Databricks!"
        fi
    else
        print_error "Could not retrieve private subnet information"
    fi
    
    # Check route tables
    print_header "User-Defined Routes (UDR)"
    
    PUBLIC_ROUTE_TABLE=$(echo "$PUBLIC_SUBNET_INFO" | jq -r '.routeTable.id // "none"')
    
    if [ "$PUBLIC_ROUTE_TABLE" != "none" ]; then
        ROUTE_TABLE_NAME=$(basename $PUBLIC_ROUTE_TABLE)
        ROUTE_TABLE_RG=$(echo $PUBLIC_ROUTE_TABLE | cut -d'/' -f5)
        
        print_success "Route table found: $ROUTE_TABLE_NAME"
        
        echo -e "\n  ${BOLD}Routes:${NC}"
        az network route-table route list \
            --resource-group "$ROUTE_TABLE_RG" \
            --route-table-name "$ROUTE_TABLE_NAME" \
            --output table
    else
        print_info "No route table attached to public subnet"
    fi
    
else
    print_header "Standard Deployment"
    print_info "Workspace uses standard deployment (no VNet injection)"
    print_info "Network configuration managed by Azure Databricks"
fi

# Summary
print_header "Summary"

if [ "$VNET_INJECTED" = true ]; then
    echo "VNet Injection: Enabled"
    echo "VNet: $VNET_NAME"
    echo "Public Subnet: $PUBLIC_SUBNET_NAME"
    echo "Private Subnet: $PRIVATE_SUBNET_NAME"
    echo ""
    echo "Key items validated:"
    echo "  ✓ Workspace configuration"
    echo "  ✓ VNet and subnet configuration"
    echo "  ✓ Subnet delegations"
    echo "  ✓ NSG rules"
    echo "  ✓ Route tables"
else
    echo "VNet Injection: Disabled"
    echo "Deployment: Standard"
fi

echo -e "\n${BOLD}For detailed troubleshooting, review:${NC}"
echo "  • NSG rules should allow AzureDatabricks service tag"
echo "  • Subnets should be delegated to Microsoft.Databricks/workspaces"
echo "  • Route tables should not block required Databricks traffic"
echo "  • Check Azure Databricks documentation for complete requirements"

print_info "\nCompleted: $(date)"
