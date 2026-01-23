"""
Azure Databricks - DNS Configuration Diagnostics
================================================

Tests DNS resolution for Databricks networking including:
- Workspace DNS resolution
- Control plane endpoints
- Storage account DNS
- Custom DNS servers
- Public vs Private DNS

Run in: Databricks Notebook
Time: ~30 seconds

Usage:
  Just run the cell - minimal configuration needed
"""

import socket
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================================================
# CONFIGURATION - SET BEFORE exec() OR MODIFY HERE
# ============================================================================

# Automatically detect workspace URL (or set manually)
if 'WORKSPACE_URL' not in globals():
    try:
        WORKSPACE_URL = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get("browserHostName").get()
    except:
        WORKSPACE_URL = "adb-xxxxx.xx.azuredatabricks.net"  # Set manually if needed

# Additional domains to test
if 'CUSTOM_DOMAINS' not in globals():
    CUSTOM_DOMAINS = [
        "yourdomain.com",
        "api.yourdomain.com",
    ]

# Storage accounts to test
if 'STORAGE_ACCOUNTS' not in globals():
    STORAGE_ACCOUNTS = [
        "yourstorageaccount",
    ]

# Test control plane endpoints
if 'TEST_CONTROL_PLANE' not in globals():
    TEST_CONTROL_PLANE = True

# ============================================================================
# SCRIPT
# ============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}")
    print(f" {text}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(text, indent=0):
    print(f"{'  '*indent}{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text, indent=0):
    print(f"{'  '*indent}{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text, indent=0):
    print(f"{'  '*indent}{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text, indent=0):
    print(f"{'  '*indent}{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def is_private_ip(ip: str) -> bool:
    """Check if IP is private"""
    try:
        parts = [int(p) for p in ip.split('.')]
        first, second = parts[0], parts[1]
        return (first == 10 or 
                (first == 172 and 16 <= second <= 31) or 
                (first == 192 and second == 168) or
                first == 127)
    except:
        return False

def test_dns_resolution(domain: str, description: str = None) -> Dict:
    """Test DNS resolution for a domain"""
    desc = description or domain
    try:
        start = time.time()
        ip = socket.gethostbyname(domain)
        elapsed = time.time() - start
        
        is_private = is_private_ip(ip)
        
        print_success(f"{desc}", indent=1)
        print(f"    Domain: {domain}")
        print(f"    IP: {ip} ({'Private' if is_private else 'Public'})")
        print(f"    Time: {elapsed:.3f}s")
        
        return {
            "domain": domain,
            "description": desc,
            "ip": ip,
            "is_private": is_private,
            "resolution_time": elapsed,
            "status": "success"
        }
    except Exception as e:
        print_error(f"{desc}: {e}", indent=1)
        return {
            "domain": domain,
            "description": desc,
            "error": str(e),
            "status": "failed"
        }

def main():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Azure Databricks - DNS Configuration Diagnostics                   ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_results = []
    
    # Test 1: Workspace DNS
    print_header("Workspace DNS Resolution")
    result = test_dns_resolution(WORKSPACE_URL, "Databricks Workspace")
    all_results.append(result)
    
    # Test 2: Control Plane Endpoints
    if TEST_CONTROL_PLANE:
        print_header("Control Plane Endpoints")
        
        # Extract region from workspace URL
        region_codes = {
            "eastus": ["tunnel.eastus.azuredatabricks.net", "eastus.azuredatabricks.net"],
            "westus": ["tunnel.westus.azuredatabricks.net", "westus.azuredatabricks.net"],
            "westeurope": ["tunnel.westeurope.azuredatabricks.net", "westeurope.azuredatabricks.net"],
        }
        
        # Try to determine region from workspace URL
        detected_region = None
        for region, _ in region_codes.items():
            if region in WORKSPACE_URL:
                detected_region = region
                break
        
        if detected_region:
            print_info(f"Detected region: {detected_region}")
            for endpoint in region_codes[detected_region]:
                result = test_dns_resolution(endpoint, f"Control Plane - {endpoint}")
                all_results.append(result)
        else:
            print_warning("Could not detect region from workspace URL")
            print_info("Testing common endpoints...")
            result = test_dns_resolution("tunnel.eastus.azuredatabricks.net", "Control Plane (East US sample)")
            all_results.append(result)
    
    # Test 3: Storage Accounts
    if STORAGE_ACCOUNTS:
        print_header("Storage Account DNS")
        for storage in STORAGE_ACCOUNTS:
            result = test_dns_resolution(f"{storage}.dfs.core.windows.net", f"ADLS Gen2 - {storage}")
            all_results.append(result)
            result = test_dns_resolution(f"{storage}.blob.core.windows.net", f"Blob Storage - {storage}")
            all_results.append(result)
    
    # Test 4: Custom Domains
    if CUSTOM_DOMAINS:
        print_header("Custom Domains")
        for domain in CUSTOM_DOMAINS:
            result = test_dns_resolution(domain, f"Custom - {domain}")
            all_results.append(result)
    
    # Test 5: External DNS (baseline)
    print_header("External DNS (Baseline)")
    external_domains = [
        ("www.microsoft.com", "Microsoft"),
        ("azure.microsoft.com", "Azure Portal"),
        ("8.8.8.8", "Google DNS"),
    ]
    for domain, desc in external_domains:
        result = test_dns_resolution(domain, desc)
        all_results.append(result)
    
    # Summary
    print_header("Summary")
    
    success = sum(1 for r in all_results if r["status"] == "success")
    failed = sum(1 for r in all_results if r["status"] == "failed")
    private_count = sum(1 for r in all_results if r.get("is_private", False))
    
    print(f"Total tests: {len(all_results)}")
    print(f"Successful: {Colors.GREEN}{success}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{failed}{Colors.RESET}")
    print(f"Private IPs: {private_count}")
    print(f"Public IPs: {len(all_results) - private_count - failed}")
    
    # Key findings
    print_header("Key Findings")
    
    workspace_result = next((r for r in all_results if r.get("domain") == WORKSPACE_URL), None)
    if workspace_result and workspace_result["status"] == "success":
        if workspace_result["is_private"]:
            print_success("Workspace uses Private Link (private IP)")
        else:
            print_info("Workspace uses public endpoint")
    
    # Check if control plane is private
    control_plane_results = [r for r in all_results if "tunnel" in r.get("domain", "")]
    if control_plane_results:
        all_private = all(r.get("is_private", False) for r in control_plane_results if r["status"] == "success")
        if all_private:
            print_success("Control plane uses Back-end Private Link")
        else:
            print_info("Control plane uses public endpoints")
    
    # Check storage
    storage_results = [r for r in all_results if any(s in r.get("domain", "") for s in STORAGE_ACCOUNTS)]
    if storage_results:
        storage_private = [r for r in storage_results if r.get("is_private", False) and r["status"] == "success"]
        if storage_private:
            print_success(f"Storage accounts use Private Endpoints ({len(storage_private)} endpoints)")
        else:
            print_info("Storage accounts use public endpoints")
    
    # Export JSON
    print_header("Detailed Results (JSON)")
    print(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "test": "dns_diagnostics",
        "workspace": WORKSPACE_URL,
        "summary": {
            "total": len(all_results),
            "success": success,
            "failed": failed,
            "private_ips": private_count
        },
        "results": all_results
    }, indent=2))
    
    print(f"\n{Colors.BOLD}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
