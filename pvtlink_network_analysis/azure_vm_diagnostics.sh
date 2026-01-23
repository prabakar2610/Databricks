#!/bin/bash

################################################################################
# Azure VM Private Link Connectivity Diagnostics
################################################################################
#
# This script should be run on an Azure VM in the same VNet as your Private
# Endpoint to compare results with Databricks connectivity tests.
#
# Usage:
#   1. Copy this script to your Azure VM
#   2. Make it executable: chmod +x azure_vm_diagnostics.sh
#   3. Update the CONFIGURATION section below
#   4. Run: ./azure_vm_diagnostics.sh
#   5. Compare results with Databricks test output
#
# Requirements:
#   - dig (dnsutils package)
#   - nc (netcat)
#   - curl
#   Optional: nmap, tcptraceroute
#
# Author: Azure Private Link Troubleshooting Guide
# Version: 2.0
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

################################################################################
# CONFIGURATION - UPDATE THESE VALUES
################################################################################

# Domains to test (space-separated)
DOMAINS_TO_TEST=(
    "api.internal.contoso.com:443"
    "api.internal.contoso.com:80"
)

# Private DNS Zone name
PRIVATE_DNS_ZONE="internal.contoso.com"

# Expected Load Balancer private IP
EXPECTED_LB_IP="10.0.1.100"

# Expected IP prefix (e.g., "10.0")
EXPECTED_IP_PREFIX="10.0"

# Connection timeout in seconds
TIMEOUT=5

# Enable advanced diagnostics (requires additional tools)
ENABLE_ADVANCED_DIAGNOSTICS=false

################################################################################
# DO NOT MODIFY BELOW THIS LINE
################################################################################

# Global variables
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0
TEST_START_TIME=$(date +%s)

# Output functions
print_header() {
    echo -e "\n${CYAN}${BOLD}================================================================================"
    echo -e " $1"
    echo -e "================================================================================${NC}\n"
}

print_subheader() {
    echo -e "\n${BLUE}${BOLD}--------------------------------------------------------------------------------"
    echo -e " $1"
    echo -e "--------------------------------------------------------------------------------${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_TESTS++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_TESTS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_metric() {
    echo -e "  ${BOLD}$1:${NC} $2"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. Some tests may behave differently."
    fi
}

# Check required tools
check_requirements() {
    print_header "Checking Requirements"
    
    local required_tools=("dig" "nc" "curl" "ping")
    local optional_tools=("nmap" "tcptraceroute" "traceroute" "nslookup")
    local missing_required=()
    local missing_optional=()
    
    echo -e "${BOLD}Required Tools:${NC}"
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool: installed"
        else
            print_error "$tool: NOT FOUND"
            missing_required+=("$tool")
        fi
    done
    
    echo -e "\n${BOLD}Optional Tools:${NC}"
    for tool in "${optional_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool: installed"
        else
            print_info "$tool: not installed (optional)"
            missing_optional+=("$tool")
        fi
    done
    
    if [ ${#missing_required[@]} -ne 0 ]; then
        echo -e "\n${RED}${BOLD}ERROR: Missing required tools!${NC}"
        echo -e "${YELLOW}Install missing tools:${NC}"
        echo "  Ubuntu/Debian: sudo apt-get install dnsutils netcat curl iputils-ping"
        echo "  RHEL/CentOS: sudo yum install bind-utils nmap-ncat curl iputils"
        exit 1
    fi
    
    if [ ${#missing_optional[@]} -ne 0 ]; then
        echo -e "\n${YELLOW}Optional tools missing. Some advanced diagnostics will be skipped.${NC}"
        echo "  Ubuntu/Debian: sudo apt-get install nmap tcptraceroute traceroute"
        echo "  RHEL/CentOS: sudo yum install nmap traceroute"
    fi
}

# Get system information
print_system_info() {
    print_header "System Information"
    
    print_metric "Hostname" "$(hostname)"
    print_metric "OS" "$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    print_metric "Kernel" "$(uname -r)"
    print_metric "Date/Time" "$(date)"
    
    echo -e "\n${BOLD}Network Interfaces:${NC}"
    ip -br addr show | while read line; do
        echo "  $line"
    done
    
    echo -e "\n${BOLD}Default Route:${NC}"
    ip route show default
    
    echo -e "\n${BOLD}DNS Configuration:${NC}"
    print_metric "Nameservers" "$(grep nameserver /etc/resolv.conf | awk '{print $2}' | tr '\n' ' ')"
    if [ -f /etc/resolv.conf ]; then
        cat /etc/resolv.conf | grep -v '^#' | grep -v '^$'
    fi
}

# Test DNS resolution
test_dns_resolution() {
    local hostname=$1
    local result=""
    
    print_info "Testing DNS resolution for: $hostname"
    
    # Test with dig (detailed)
    if command -v dig &> /dev/null; then
        echo -e "\n${BOLD}  Using dig:${NC}"
        local dig_output=$(dig +short "$hostname" A 2>&1)
        
        if [ -n "$dig_output" ]; then
            echo "$dig_output" | while read ip; do
                if [[ $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                    echo "    IP: $ip"
                    
                    # Check if private IP
                    if is_private_ip "$ip"; then
                        print_success "      Private IP detected"
                    else
                        print_error "      PUBLIC IP detected - Private Link NOT working!"
                    fi
                    
                    # Check if matches expected
                    if [ -n "$EXPECTED_LB_IP" ] && [ "$ip" == "$EXPECTED_LB_IP" ]; then
                        print_success "      Matches expected LB IP"
                    elif [ -n "$EXPECTED_LB_IP" ]; then
                        print_warning "      Does not match expected LB IP: $EXPECTED_LB_IP"
                    fi
                fi
            done
            
            # Full dig output for debugging
            echo -e "\n  ${BOLD}Full dig output:${NC}"
            dig "$hostname" A | sed 's/^/    /'
        else
            print_error "  dig: No DNS response"
            return 1
        fi
    fi
    
    # Test with nslookup
    if command -v nslookup &> /dev/null; then
        echo -e "\n${BOLD}  Using nslookup:${NC}"
        nslookup "$hostname" 2>&1 | sed 's/^/    /'
    fi
    
    # Test with host
    if command -v host &> /dev/null; then
        echo -e "\n${BOLD}  Using host:${NC}"
        host "$hostname" 2>&1 | sed 's/^/    /'
    fi
    
    return 0
}

# Check if IP is private
is_private_ip() {
    local ip=$1
    local first_octet=$(echo "$ip" | cut -d'.' -f1)
    local second_octet=$(echo "$ip" | cut -d'.' -f2)
    
    if [ "$first_octet" == "10" ]; then
        return 0
    elif [ "$first_octet" == "172" ] && [ "$second_octet" -ge 16 ] && [ "$second_octet" -le 31 ]; then
        return 0
    elif [ "$first_octet" == "192" ] && [ "$second_octet" == "168" ]; then
        return 0
    elif [ "$first_octet" == "127" ]; then
        return 0
    fi
    
    return 1
}

# Test TCP connectivity
test_tcp_connection() {
    local hostname=$1
    local port=$2
    
    print_info "Testing TCP connection to: $hostname:$port"
    
    # Get IP first
    local ip=$(dig +short "$hostname" A | head -n1)
    if [ -z "$ip" ]; then
        print_error "  Cannot test TCP - DNS resolution failed"
        return 1
    fi
    
    print_metric "  Resolved IP" "$ip"
    
    # Test with netcat
    echo -e "\n${BOLD}  Using netcat:${NC}"
    local start_time=$(date +%s.%N)
    
    if timeout $TIMEOUT nc -zv "$hostname" "$port" 2>&1 | sed 's/^/    /'; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc)
        print_success "  Connection successful (${duration}s)"
    else
        print_error "  Connection failed or timeout"
        return 1
    fi
    
    # Test with curl (if HTTPS)
    if [ "$port" == "443" ]; then
        echo -e "\n${BOLD}  Using curl (HTTPS):${NC}"
        local curl_output=$(curl -k -v -m $TIMEOUT "https://$hostname" 2>&1)
        echo "$curl_output" | grep -E "Connected to|SSL|certificate" | sed 's/^/    /'
    fi
    
    # Test with telnet if available
    if command -v telnet &> /dev/null; then
        echo -e "\n${BOLD}  Using telnet:${NC}"
        (echo "quit"; sleep 1) | timeout $TIMEOUT telnet "$hostname" "$port" 2>&1 | head -n5 | sed 's/^/    /'
    fi
    
    return 0
}

# Advanced network diagnostics
run_advanced_diagnostics() {
    local hostname=$1
    local port=$2
    
    print_subheader "Advanced Diagnostics: $hostname:$port"
    
    # Traceroute
    if command -v traceroute &> /dev/null; then
        print_info "Traceroute to $hostname:"
        timeout 30 traceroute -m 15 "$hostname" 2>&1 | sed 's/^/  /'
    fi
    
    # TCP Traceroute (if available)
    if command -v tcptraceroute &> /dev/null; then
        print_info "TCP Traceroute to $hostname:$port:"
        timeout 30 tcptraceroute "$hostname" "$port" 2>&1 | sed 's/^/  /'
    fi
    
    # MTR (if available)
    if command -v mtr &> /dev/null; then
        print_info "MTR report to $hostname:"
        mtr -r -c 5 "$hostname" 2>&1 | sed 's/^/  /'
    fi
    
    # Port scan with nmap (if available)
    if command -v nmap &> /dev/null; then
        print_info "Nmap port scan:"
        local ip=$(dig +short "$hostname" A | head -n1)
        if [ -n "$ip" ]; then
            nmap -Pn -p 80,443,8080,8443 "$ip" 2>&1 | sed 's/^/  /'
        fi
    fi
}

# Test a domain:port combination
test_domain() {
    local domain_port=$1
    local hostname=$(echo "$domain_port" | cut -d':' -f1)
    local port=$(echo "$domain_port" | cut -d':' -f2)
    
    print_subheader "Testing: $hostname:$port"
    
    ((TOTAL_TESTS++))
    
    # DNS Resolution
    test_dns_resolution "$hostname"
    local dns_result=$?
    
    # TCP Connection
    if [ $dns_result -eq 0 ]; then
        test_tcp_connection "$hostname" "$port"
        local tcp_result=$?
    else
        print_error "Skipping TCP test due to DNS failure"
    fi
    
    # Advanced diagnostics
    if [ "$ENABLE_ADVANCED_DIAGNOSTICS" == "true" ]; then
        run_advanced_diagnostics "$hostname" "$port"
    fi
}

# Test external connectivity
test_external_connectivity() {
    print_header "External Connectivity Test"
    
    print_info "Testing connectivity to external services..."
    
    # Test Google DNS
    echo -e "\n${BOLD}Testing: 8.8.8.8 (Google DNS)${NC}"
    if ping -c 3 -W 2 8.8.8.8 &> /dev/null; then
        print_success "Can reach Google DNS"
    else
        print_error "Cannot reach Google DNS"
    fi
    
    # Test external HTTP
    echo -e "\n${BOLD}Testing: www.microsoft.com${NC}"
    if curl -s -m 5 --head https://www.microsoft.com | head -n1 | grep -q "200"; then
        print_success "Can reach Microsoft (HTTPS)"
    else
        print_warning "Cannot reach Microsoft or non-200 response"
    fi
    
    # Get public IP
    echo -e "\n${BOLD}Public IP Detection:${NC}"
    local public_ip=$(curl -s -m 5 ifconfig.me)
    if [ -n "$public_ip" ]; then
        print_metric "Public IP" "$public_ip"
        if is_private_ip "$public_ip"; then
            print_warning "Public IP appears to be private (NAT or proxy?)"
        fi
    else
        print_warning "Could not determine public IP"
    fi
}

# Check Azure VM metadata
check_azure_metadata() {
    print_header "Azure VM Metadata"
    
    print_info "Querying Azure Instance Metadata Service..."
    
    # Get metadata
    local metadata=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance?api-version=2021-02-01" 2>/dev/null)
    
    if [ -n "$metadata" ]; then
        print_success "Successfully retrieved Azure metadata"
        
        echo -e "\n${BOLD}VM Information:${NC}"
        echo "$metadata" | grep -o '"vmId":"[^"]*"' | sed 's/"vmId":"/  VM ID: /' | sed 's/"$//'
        echo "$metadata" | grep -o '"location":"[^"]*"' | sed 's/"location":"/  Location: /' | sed 's/"$//'
        echo "$metadata" | grep -o '"vmSize":"[^"]*"' | sed 's/"vmSize":"/  VM Size: /' | sed 's/"$//'
        
        echo -e "\n${BOLD}Network Information:${NC}"
        echo "$metadata" | grep -o '"privateIpAddress":"[^"]*"' | sed 's/"privateIpAddress":"/  Private IP: /' | sed 's/"$//'
        echo "$metadata" | grep -o '"subnet":"[^"]*"' | sed 's/"subnet":"/  Subnet: /' | sed 's/"$//'
        echo "$metadata" | grep -o '"virtualNetwork":"[^"]*"' | sed 's/"virtualNetwork":"/  VNet: /' | sed 's/"$//'
    else
        print_warning "Not running on Azure VM or metadata service unavailable"
    fi
}

# Check network security
check_network_security() {
    print_header "Network Security Check"
    
    # Check iptables (if available)
    if command -v iptables &> /dev/null && [ "$EUID" -eq 0 ]; then
        print_info "IPTables rules:"
        iptables -L -n | head -n 20 | sed 's/^/  /'
    else
        print_info "IPTables check skipped (requires root or iptables not available)"
    fi
    
    # Check firewalld (if available)
    if command -v firewall-cmd &> /dev/null; then
        print_info "Firewalld status:"
        firewall-cmd --state 2>&1 | sed 's/^/  /'
    fi
    
    # Check UFW (if available)
    if command -v ufw &> /dev/null; then
        print_info "UFW status:"
        ufw status 2>&1 | sed 's/^/  /'
    fi
}

# Generate summary
print_summary() {
    print_header "Diagnostic Summary"
    
    local test_end_time=$(date +%s)
    local test_duration=$((test_end_time - TEST_START_TIME))
    
    print_metric "Total tests" "$TOTAL_TESTS"
    print_metric "Passed" "$PASSED_TESTS"
    print_metric "Failed" "$FAILED_TESTS"
    print_metric "Warnings" "$WARNINGS"
    print_metric "Duration" "${test_duration}s"
    
    echo -e "\n${BOLD}Configuration Checked:${NC}"
    print_metric "Private DNS Zone" "$PRIVATE_DNS_ZONE"
    print_metric "Expected LB IP" "$EXPECTED_LB_IP"
    print_metric "Expected IP Prefix" "$EXPECTED_IP_PREFIX.x.x"
    
    echo -e "\n${BOLD}Recommendations:${NC}"
    
    if [ $FAILED_TESTS -gt 0 ]; then
        echo -e "\n${RED}${BOLD}Issues detected!${NC}"
        echo -e "  1. Review the detailed output above"
        echo -e "  2. Compare with Databricks test results"
        echo -e "  3. Check Azure Portal for:"
        echo -e "     - Private DNS Zone configuration"
        echo -e "     - Private Endpoint status"
        echo -e "     - Load Balancer health probes"
        echo -e "     - NSG rules"
        echo -e "  4. Verify NCC configuration in Databricks"
    else
        echo -e "\n${GREEN}${BOLD}All tests passed from Azure VM!${NC}"
        echo -e "  If Databricks tests are failing:"
        echo -e "  1. NCC may not be properly attached to workspace"
        echo -e "  2. NCC domain configuration may be incorrect"
        echo -e "  3. Private Endpoint may not be in Databricks VNet"
    fi
}

# Main execution
main() {
    echo -e "${MAGENTA}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                            ║"
    echo "║           Azure VM Private Link Connectivity Diagnostics                   ║"
    echo "║                                                                            ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo "Test started at: $(date)"
    echo ""
    
    # Pre-flight checks
    check_root
    check_requirements
    
    # System information
    print_system_info
    
    # Azure metadata
    check_azure_metadata
    
    # External connectivity
    test_external_connectivity
    
    # Network security
    check_network_security
    
    # Test each domain
    print_header "Private Link Connectivity Tests"
    
    for domain_port in "${DOMAINS_TO_TEST[@]}"; do
        test_domain "$domain_port"
    done
    
    # Summary
    print_summary
    
    echo -e "\n${BOLD}Test completed at: $(date)${NC}\n"
}

# Run main function
main
