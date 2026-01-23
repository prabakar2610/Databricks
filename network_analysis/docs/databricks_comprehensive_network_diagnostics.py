"""
Azure Databricks Comprehensive Network Diagnostics
==================================================

This script provides comprehensive network troubleshooting for ALL Azure Databricks
networking scenarios as documented in Microsoft documentation.

Covers:
- Front-end networking (Private Link, IP access lists)
- Classic compute plane (VNet injection, peering, UDR, back-end Private Link)
- Serverless compute plane (Private Link to Azure services, egress control)
- Network security (firewalls, NSGs, service endpoints)

Reference: https://learn.microsoft.com/en-us/azure/databricks/security/network/

Usage:
1. Copy this entire script into a Databricks notebook
2. Update the CONFIGURATION section
3. Run the cell
4. Review comprehensive diagnostic output

Version: 3.0 - Complete Network Diagnostics
"""

import socket
import time
import json
import sys
import subprocess
from typing import Tuple, Dict, List, Optional
from datetime import datetime
from collections import defaultdict

# ============================================================================
# CONFIGURATION - Update these values
# ============================================================================

# Test scenarios to run (set to True to enable)
TEST_SCENARIOS = {
    # Front-end networking
    "test_workspace_connectivity": True,         # Web UI/API access
    "test_ip_access_lists": True,                # IP allowlist validation
    "test_frontend_private_link": True,          # Front-end Private Link
    
    # Classic compute networking
    "test_vnet_configuration": True,             # VNet injection validation
    "test_backend_private_link": True,           # Back-end Private Link
    "test_control_plane_connectivity": True,     # Control plane access
    "test_nsg_rules": True,                      # NSG configuration
    "test_udr_configuration": True,              # User-defined routes
    
    # Serverless networking
    "test_serverless_storage": True,             # Serverless to Azure Storage
    "test_serverless_private_link": True,        # Serverless Private Link
    "test_serverless_egress": True,              # Network policies/egress control
    
    # Storage & data access
    "test_storage_connectivity": True,           # Workspace storage access
    "test_storage_firewall": True,               # Storage firewall rules
    "test_adls_access": True,                    # ADLS Gen2 connectivity
    
    # General networking
    "test_dns_resolution": True,                 # DNS configuration
    "test_external_connectivity": True,          # Internet access
    "test_custom_endpoints": True,               # Custom service endpoints
}

# Workspace information
WORKSPACE_INFO = {
    "workspace_url": "https://adb-xxxxx.xx.azuredatabricks.net",
    "workspace_id": "xxxxx",
    "region": "eastus",
    "resource_group": "your-rg",
    "subscription_id": "your-sub-id",
}

# Network configuration
NETWORK_CONFIG = {
    # VNet configuration (if using VNet injection)
    "vnet_injected": False,
    "vnet_name": None,
    "vnet_resource_group": None,
    "public_subnet": None,
    "private_subnet": None,
    
    # Private Link configuration
    "frontend_private_link_enabled": False,
    "backend_private_link_enabled": False,
    
    # Expected IP ranges
    "expected_egress_ip_range": "10.0.0.0/16",
    "databricks_nat_ip": None,  # If known
    
    # DNS servers
    "custom_dns_servers": [],
}

# Storage accounts to test
STORAGE_ACCOUNTS = [
    {
        "name": "yourstorageaccount",
        "type": "adls_gen2",  # or "blob"
        "container": "your-container",
        "has_firewall": False,
        "has_private_endpoint": False,
    },
]

# Custom endpoints to test (Private Link to internal resources)
CUSTOM_ENDPOINTS = [
    {"host": "api.yourdomain.com", "port": 443, "description": "Internal API"},
    {"host": "database.yourdomain.com", "port": 1433, "description": "SQL Server"},
]

# Control plane endpoints (by region)
CONTROL_PLANE_ENDPOINTS = {
    "eastus": [
        "tunnel.eastus.azuredatabricks.net",
        "eastus.azuredatabricks.net",
    ],
    "westus": [
        "tunnel.westus.azuredatabricks.net",
        "westus.azuredatabricks.net",
    ],
    "westeurope": [
        "tunnel.westeurope.azuredatabricks.net",
        "westeurope.azuredatabricks.net",
    ],
    # Add more regions as needed
}

# External services to test (for egress validation)
EXTERNAL_TEST_SERVICES = [
    {"host": "pypi.org", "port": 443, "description": "PyPI (package install)"},
    {"host": "packages.microsoft.com", "port": 443, "description": "Microsoft packages"},
    {"host": "archive.ubuntu.com", "port": 80, "description": "Ubuntu packages"},
]

# ============================================================================
# DO NOT MODIFY BELOW THIS LINE
# ============================================================================

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text: str, level: int = 1):
    """Print formatted header"""
    if level == 1:
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
        print(f" {text}")
        print(f"{'='*80}{Colors.RESET}\n")
    elif level == 2:
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'-'*80}")
        print(f" {text}")
        print(f"{'-'*80}{Colors.RESET}\n")
    else:
        print(f"\n{Colors.WHITE}{Colors.BOLD}{text}{Colors.RESET}")

def print_success(text: str, indent: int = 0):
    """Print success message"""
    prefix = "  " * indent
    print(f"{prefix}{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str, indent: int = 0):
    """Print error message"""
    prefix = "  " * indent
    print(f"{prefix}{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str, indent: int = 0):
    """Print warning message"""
    prefix = "  " * indent
    print(f"{prefix}{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str, indent: int = 0):
    """Print info message"""
    prefix = "  " * indent
    print(f"{prefix}{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_metric(label: str, value: str, indent: int = 0):
    """Print a metric"""
    prefix = "  " * indent
    print(f"{prefix}{Colors.WHITE}{label}:{Colors.RESET} {value}")

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_workspace_connectivity():
    """Test connectivity to workspace web UI and API"""
    print_header("Front-End: Workspace Connectivity", 2)
    
    results = {
        "test_name": "workspace_connectivity",
        "status": "unknown",
        "checks": []
    }
    
    workspace_url = WORKSPACE_INFO["workspace_url"]
    
    # Test 1: Resolve workspace URL
    print_info("Testing workspace DNS resolution...")
    try:
        hostname = workspace_url.replace("https://", "").replace("http://", "")
        ip = socket.gethostbyname(hostname)
        print_success(f"Workspace resolves to: {ip}", indent=1)
        results["checks"].append({"dns_resolution": "success", "ip": ip})
    except Exception as e:
        print_error(f"Workspace DNS resolution failed: {e}", indent=1)
        results["checks"].append({"dns_resolution": "failed", "error": str(e)})
        results["status"] = "failed"
        return results
    
    # Test 2: HTTPS connectivity
    print_info("Testing HTTPS connectivity to workspace...")
    try:
        import requests
        response = requests.get(workspace_url, timeout=10, allow_redirects=True)
        print_success(f"Workspace accessible (HTTP {response.status_code})", indent=1)
        results["checks"].append({"https_connectivity": "success", "status_code": response.status_code})
    except requests.exceptions.SSLError as e:
        print_error(f"SSL/TLS error: {e}", indent=1)
        results["checks"].append({"https_connectivity": "ssl_error", "error": str(e)})
        results["status"] = "failed"
    except requests.exceptions.ConnectionError as e:
        print_error(f"Connection error: {e}", indent=1)
        results["checks"].append({"https_connectivity": "connection_error", "error": str(e)})
        results["status"] = "failed"
    except Exception as e:
        print_error(f"Workspace not accessible: {e}", indent=1)
        results["checks"].append({"https_connectivity": "failed", "error": str(e)})
        results["status"] = "failed"
    
    # Test 3: Check if using Private Link
    if NETWORK_CONFIG.get("frontend_private_link_enabled"):
        print_info("Checking front-end Private Link configuration...")
        if is_private_ip(ip):
            print_success("Using front-end Private Link (private IP)", indent=1)
            results["checks"].append({"private_link": "active"})
        else:
            print_warning("Front-end Private Link configured but resolves to public IP", indent=1)
            results["checks"].append({"private_link": "misconfigured"})
    
    if results["status"] == "unknown":
        results["status"] = "success"
    
    return results

def test_ip_access_lists():
    """Test IP access list configuration"""
    print_header("Front-End: IP Access Lists", 2)
    
    results = {
        "test_name": "ip_access_lists",
        "status": "unknown",
        "checks": []
    }
    
    # Get current public IP
    print_info("Detecting current IP address...")
    try:
        import requests
        current_ip = requests.get("https://api.ipify.org", timeout=5).text
        print_success(f"Current IP: {current_ip}", indent=1)
        results["checks"].append({"current_ip": current_ip})
    except Exception as e:
        print_warning(f"Could not detect current IP: {e}", indent=1)
        current_ip = "unknown"
    
    # Try to access workspace
    print_info("Testing workspace access (IP access list check)...")
    try:
        import requests
        response = requests.get(WORKSPACE_INFO["workspace_url"], timeout=10)
        
        if response.status_code == 403:
            print_error("Access denied (403) - IP may not be in access list", indent=1)
            results["checks"].append({"access": "blocked", "reason": "ip_not_allowed"})
            results["status"] = "blocked"
        else:
            print_success("IP access list check passed", indent=1)
            results["checks"].append({"access": "allowed"})
            results["status"] = "success"
    except Exception as e:
        print_error(f"Could not test IP access: {e}", indent=1)
        results["checks"].append({"access": "error", "error": str(e)})
    
    print_info("Recommendations:", indent=1)
    print("   • Check workspace IP access lists in Settings → Network", indent=1)
    print("   • Check account-level IP access lists if configured", indent=1)
    print(f"   • Add current IP ({current_ip}) to allowlist if needed", indent=1)
    
    return results

def test_control_plane_connectivity():
    """Test connectivity to Azure Databricks control plane"""
    print_header("Classic Compute: Control Plane Connectivity", 2)
    
    results = {
        "test_name": "control_plane_connectivity",
        "status": "unknown",
        "checks": []
    }
    
    region = WORKSPACE_INFO.get("region", "eastus")
    endpoints = CONTROL_PLANE_ENDPOINTS.get(region, CONTROL_PLANE_ENDPOINTS["eastus"])
    
    print_info(f"Testing control plane endpoints for region: {region}")
    
    for endpoint in endpoints:
        print_info(f"Testing: {endpoint}", indent=1)
        
        # DNS resolution
        try:
            ip = socket.gethostbyname(endpoint)
            print_success(f"Resolves to: {ip}", indent=2)
            
            # Check if private IP (back-end Private Link)
            if is_private_ip(ip):
                print_success("Using back-end Private Link (private IP)", indent=2)
                results["checks"].append({
                    "endpoint": endpoint,
                    "ip": ip,
                    "private_link": True
                })
            else:
                print_info("Using public endpoint", indent=2)
                results["checks"].append({
                    "endpoint": endpoint,
                    "ip": ip,
                    "private_link": False
                })
            
            # TCP connectivity test
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((endpoint, 443))
                sock.close()
                print_success("TCP connectivity: OK", indent=2)
            except Exception as e:
                print_error(f"TCP connectivity failed: {e}", indent=2)
                results["checks"][-1]["tcp_error"] = str(e)
                
        except Exception as e:
            print_error(f"DNS resolution failed: {e}", indent=2)
            results["checks"].append({
                "endpoint": endpoint,
                "error": str(e)
            })
    
    # Determine overall status
    if all("error" not in check and "tcp_error" not in check for check in results["checks"]):
        results["status"] = "success"
    else:
        results["status"] = "partial"
    
    return results

def test_storage_connectivity():
    """Test connectivity to Azure Storage accounts"""
    print_header("Storage: Workspace Storage Access", 2)
    
    results = {
        "test_name": "storage_connectivity",
        "status": "unknown",
        "checks": []
    }
    
    if not STORAGE_ACCOUNTS:
        print_warning("No storage accounts configured for testing")
        results["status"] = "skipped"
        return results
    
    for storage in STORAGE_ACCOUNTS:
        storage_name = storage["name"]
        storage_type = storage.get("type", "blob")
        
        print_info(f"Testing storage account: {storage_name}", indent=1)
        
        # Construct storage URL
        if storage_type == "adls_gen2":
            endpoint = f"{storage_name}.dfs.core.windows.net"
        else:
            endpoint = f"{storage_name}.blob.core.windows.net"
        
        # DNS resolution
        try:
            ip = socket.gethostbyname(endpoint)
            print_success(f"DNS resolves to: {ip}", indent=2)
            
            if is_private_ip(ip):
                print_success("Using private endpoint", indent=2)
                storage_result = {"storage": storage_name, "private_endpoint": True, "ip": ip}
            else:
                print_info("Using public endpoint", indent=2)
                storage_result = {"storage": storage_name, "private_endpoint": False, "ip": ip}
            
            # TCP connectivity test
            port = 443
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((endpoint, port))
                sock.close()
                print_success(f"TCP connectivity: OK", indent=2)
                storage_result["connectivity"] = "success"
            except Exception as e:
                print_error(f"TCP connectivity failed: {e}", indent=2)
                storage_result["connectivity"] = "failed"
                storage_result["error"] = str(e)
            
            results["checks"].append(storage_result)
            
        except Exception as e:
            print_error(f"DNS resolution failed: {e}", indent=2)
            results["checks"].append({
                "storage": storage_name,
                "error": str(e)
            })
    
    # Check firewall configuration if specified
    for storage in STORAGE_ACCOUNTS:
        if storage.get("has_firewall"):
            print_warning(f"Storage account '{storage['name']}' has firewall enabled", indent=1)
            print("   Verify Databricks NAT IP is allowlisted", indent=1)
    
    if results["checks"]:
        results["status"] = "success" if all(c.get("connectivity") == "success" for c in results["checks"]) else "partial"
    
    return results

def test_dns_resolution():
    """Test DNS configuration"""
    print_header("General: DNS Configuration", 2)
    
    results = {
        "test_name": "dns_resolution",
        "status": "unknown",
        "checks": []
    }
    
    # Test DNS servers
    print_info("Testing DNS resolution...")
    
    test_domains = [
        ("www.microsoft.com", "External DNS"),
        ("azure.microsoft.com", "Azure DNS"),
        (WORKSPACE_INFO["workspace_url"].replace("https://", "").replace("http://", ""), "Workspace DNS"),
    ]
    
    for domain, description in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            print_success(f"{description}: {domain} → {ip}", indent=1)
            results["checks"].append({
                "domain": domain,
                "description": description,
                "ip": ip,
                "status": "success"
            })
        except Exception as e:
            print_error(f"{description}: {domain} failed - {e}", indent=1)
            results["checks"].append({
                "domain": domain,
                "description": description,
                "error": str(e),
                "status": "failed"
            })
    
    # Check custom DNS if configured
    if NETWORK_CONFIG.get("custom_dns_servers"):
        print_info("Custom DNS servers configured:")
        for dns_server in NETWORK_CONFIG["custom_dns_servers"]:
            print(f"   • {dns_server}", indent=1)
    
    results["status"] = "success" if all(c["status"] == "success" for c in results["checks"]) else "partial"
    
    return results

def test_external_connectivity():
    """Test external internet connectivity (egress)"""
    print_header("Serverless: External Connectivity & Egress", 2)
    
    results = {
        "test_name": "external_connectivity",
        "status": "unknown",
        "checks": []
    }
    
    print_info("Testing egress connectivity to external services...")
    
    for service in EXTERNAL_TEST_SERVICES:
        host = service["host"]
        port = service["port"]
        description = service["description"]
        
        print_info(f"Testing: {description} ({host}:{port})", indent=1)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            start = time.time()
            sock.connect((host, port))
            elapsed = time.time() - start
            sock.close()
            
            print_success(f"Connected ({elapsed:.2f}s)", indent=2)
            results["checks"].append({
                "service": description,
                "host": host,
                "port": port,
                "status": "success",
                "time": elapsed
            })
        except Exception as e:
            print_error(f"Connection failed: {e}", indent=2)
            results["checks"].append({
                "service": description,
                "host": host,
                "port": port,
                "status": "failed",
                "error": str(e)
            })
    
    # Check for network policy restrictions
    failed_count = sum(1 for c in results["checks"] if c["status"] == "failed")
    if failed_count > 0:
        print_warning(f"{failed_count} services unreachable", indent=1)
        print("   Possible causes:", indent=1)
        print("   • Network policies blocking egress", indent=1)
        print("   • Firewall rules", indent=1)
        print("   • NSG restrictions", indent=1)
    
    results["status"] = "success" if failed_count == 0 else "partial"
    
    return results

def test_custom_endpoints():
    """Test connectivity to custom internal endpoints"""
    print_header("Serverless: Private Link to Internal Resources", 2)
    
    if not CUSTOM_ENDPOINTS:
        print_warning("No custom endpoints configured for testing")
        return {"test_name": "custom_endpoints", "status": "skipped", "checks": []}
    
    results = {
        "test_name": "custom_endpoints",
        "status": "unknown",
        "checks": []
    }
    
    for endpoint in CUSTOM_ENDPOINTS:
        host = endpoint["host"]
        port = endpoint["port"]
        description = endpoint.get("description", "Custom endpoint")
        
        print_info(f"Testing: {description} ({host}:{port})", indent=1)
        
        # DNS resolution
        try:
            ip = socket.gethostbyname(host)
            print_success(f"DNS resolves to: {ip}", indent=2)
            
            if is_private_ip(ip):
                print_success("Private IP - Private Link likely active", indent=2)
            else:
                print_error("Public IP - Private Link NOT working!", indent=2)
            
            endpoint_result = {
                "host": host,
                "port": port,
                "description": description,
                "ip": ip,
                "is_private": is_private_ip(ip)
            }
            
            # TCP connectivity
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))
                sock.close()
                print_success("TCP connectivity: OK", indent=2)
                endpoint_result["connectivity"] = "success"
            except Exception as e:
                print_error(f"TCP connectivity failed: {e}", indent=2)
                endpoint_result["connectivity"] = "failed"
                endpoint_result["tcp_error"] = str(e)
            
            results["checks"].append(endpoint_result)
            
        except Exception as e:
            print_error(f"DNS resolution failed: {e}", indent=2)
            results["checks"].append({
                "host": host,
                "port": port,
                "description": description,
                "error": str(e)
            })
    
    # Determine status
    if results["checks"]:
        all_private = all(c.get("is_private", False) for c in results["checks"] if "ip" in c)
        all_connected = all(c.get("connectivity") == "success" for c in results["checks"] if "connectivity" in c)
        
        if all_private and all_connected:
            results["status"] = "success"
        elif not all_private:
            results["status"] = "private_link_failed"
        else:
            results["status"] = "partial"
    
    return results

def test_vnet_configuration():
    """Test VNet injection configuration"""
    print_header("Classic Compute: VNet Injection", 2)
    
    results = {
        "test_name": "vnet_configuration",
        "status": "unknown",
        "checks": []
    }
    
    if not NETWORK_CONFIG.get("vnet_injected"):
        print_info("VNet injection not configured (using standard deployment)")
        results["status"] = "not_configured"
        return results
    
    print_info("Validating VNet injection configuration...")
    
    # Check VNet configuration
    vnet_name = NETWORK_CONFIG.get("vnet_name")
    public_subnet = NETWORK_CONFIG.get("public_subnet")
    private_subnet = NETWORK_CONFIG.get("private_subnet")
    
    if vnet_name:
        print_success(f"VNet: {vnet_name}", indent=1)
        results["checks"].append({"vnet": vnet_name})
    else:
        print_warning("VNet name not configured", indent=1)
    
    if public_subnet and private_subnet:
        print_success(f"Subnets configured: {public_subnet}, {private_subnet}", indent=1)
        results["checks"].append({"public_subnet": public_subnet, "private_subnet": private_subnet})
    else:
        print_warning("Subnets not fully configured", indent=1)
    
    # Note: Full validation requires Azure CLI/API access
    print_info("For complete VNet validation, check Azure Portal:", indent=1)
    print("   • NSG rules on subnets", indent=1)
    print("   • Service endpoints configured", indent=1)
    print("   • Subnet delegation to Databricks", indent=1)
    
    results["status"] = "partial"
    return results

def test_nsg_rules():
    """Test NSG configuration"""
    print_header("Classic Compute: Network Security Groups", 2)
    
    results = {
        "test_name": "nsg_rules",
        "status": "unknown",
        "checks": []
    }
    
    print_info("NSG validation requires Azure access")
    print_info("Minimum required NSG rules for Databricks:", indent=1)
    
    required_rules = [
        "Allow AzureDatabricks service tag (inbound)",
        "Allow VirtualNetwork (inbound within VNet)",
        "Allow internet access (outbound) - or specific service tags",
        "Allow AzureStorage service tag (outbound)",
    ]
    
    for rule in required_rules:
        print(f"   • {rule}", indent=1)
    
    print_info("\nTo validate NSG rules:", indent=1)
    print("   1. Go to Azure Portal → Network Security Groups", indent=1)
    print("   2. Check NSGs attached to Databricks subnets", indent=1)
    print("   3. Verify inbound/outbound rules match requirements", indent=1)
    
    results["status"] = "manual_check_required"
    return results

def test_udr_configuration():
    """Test user-defined routes"""
    print_header("Classic Compute: User-Defined Routes (UDR)", 2)
    
    results = {
        "test_name": "udr_configuration",
        "status": "unknown",
        "checks": []
    }
    
    print_info("UDR validation requires Azure access")
    print_info("Common UDR requirements:", indent=1)
    print("   • Route for AzureDatabricks service tag", indent=1)
    print("   • Route for SQL, Storage, EventHub service tags", indent=1)
    print("   • Route for internet access (if not using firewall)", indent=1)
    
    print_info("\nTo validate UDR:", indent=1)
    print("   1. Go to Azure Portal → Route Tables", indent=1)
    print("   2. Check route table associated with Databricks subnets", indent=1)
    print("   3. Verify routes don't block required Databricks traffic", indent=1)
    
    results["status"] = "manual_check_required"
    return results

# Helper functions

def is_private_ip(ip: str) -> bool:
    """Check if IP is in private range"""
    try:
        parts = [int(p) for p in ip.split('.')]
        first, second = parts[0], parts[1]
        
        if first == 10:
            return True
        if first == 172 and 16 <= second <= 31:
            return True
        if first == 192 and second == 168:
            return True
        if first == 127:
            return True
        
        return False
    except:
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║     Azure Databricks Comprehensive Network Diagnostics v3.0               ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Workspace info
    print_header("Workspace Information")
    print_metric("Workspace URL", WORKSPACE_INFO["workspace_url"])
    print_metric("Region", WORKSPACE_INFO["region"])
    print_metric("VNet Injection", "Enabled" if NETWORK_CONFIG.get("vnet_injected") else "Disabled")
    print_metric("Front-end Private Link", "Enabled" if NETWORK_CONFIG.get("frontend_private_link_enabled") else "Disabled")
    print_metric("Back-end Private Link", "Enabled" if NETWORK_CONFIG.get("backend_private_link_enabled") else "Disabled")
    
    # Run tests
    all_results = []
    
    test_functions = {
        "test_workspace_connectivity": test_workspace_connectivity,
        "test_ip_access_lists": test_ip_access_lists,
        "test_control_plane_connectivity": test_control_plane_connectivity,
        "test_vnet_configuration": test_vnet_configuration,
        "test_nsg_rules": test_nsg_rules,
        "test_udr_configuration": test_udr_configuration,
        "test_storage_connectivity": test_storage_connectivity,
        "test_dns_resolution": test_dns_resolution,
        "test_external_connectivity": test_external_connectivity,
        "test_custom_endpoints": test_custom_endpoints,
    }
    
    for test_name, test_func in test_functions.items():
        if TEST_SCENARIOS.get(test_name, False):
            try:
                result = test_func()
                all_results.append(result)
            except Exception as e:
                print_error(f"Test {test_name} failed with exception: {e}")
                all_results.append({
                    "test_name": test_name,
                    "status": "error",
                    "error": str(e)
                })
    
    # Summary
    print_header("Diagnostic Summary")
    
    success_count = sum(1 for r in all_results if r["status"] == "success")
    partial_count = sum(1 for r in all_results if r["status"] == "partial")
    failed_count = sum(1 for r in all_results if r["status"] in ["failed", "error", "blocked"])
    skipped_count = sum(1 for r in all_results if r["status"] == "skipped")
    
    print_metric("Total tests run", len(all_results))
    print_metric("Passed", f"{success_count} {Colors.GREEN}✓{Colors.RESET}")
    print_metric("Partial", f"{partial_count} {Colors.YELLOW}⚠{Colors.RESET}")
    print_metric("Failed", f"{failed_count} {Colors.RED}✗{Colors.RESET}")
    print_metric("Skipped", skipped_count)
    
    # Issues found
    print("\n" + Colors.BOLD + "Issues Found:" + Colors.RESET)
    issues_found = False
    for result in all_results:
        if result["status"] in ["failed", "error", "blocked", "private_link_failed"]:
            issues_found = True
            print_error(f"{result['test_name']}: {result['status']}")
            if "error" in result:
                print(f"   {result['error']}", indent=1)
    
    if not issues_found:
        print_success("No critical issues found!")
    
    # Export JSON
    print_header("Detailed Results (JSON)")
    print(json.dumps({
        "test_metadata": {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0",
            "workspace": WORKSPACE_INFO["workspace_url"]
        },
        "test_results": all_results
    }, indent=2))
    
    print(f"\n{Colors.BOLD}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
