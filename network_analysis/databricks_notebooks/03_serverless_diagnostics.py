"""
Azure Databricks - Serverless Compute Diagnostics
=================================================

Tests serverless compute networking including:
- Serverless to Azure Storage connectivity
- Serverless to external services (egress)
- Network policies validation
- Serverless Private Link status

Run in: Databricks Notebook (Serverless SQL Warehouse or Serverless Jobs)
Time: ~1 minute

Usage:
  Run this in a serverless compute context
"""

import socket
import time
import json
from datetime import datetime
from typing import Dict, List

# ============================================================================
# CONFIGURATION - SET BEFORE exec() OR MODIFY HERE
# ============================================================================

# Storage accounts to test
if 'STORAGE_ACCOUNTS' not in globals():
    STORAGE_ACCOUNTS = [
        {
            "name": "yourstorageaccount",
            "test_adls": True,
            "test_blob": True,
        },
    ]

# External services to test (egress validation)
if 'EXTERNAL_SERVICES' not in globals():
    EXTERNAL_SERVICES = [
        {"host": "pypi.org", "port": 443, "description": "PyPI (Python packages)"},
        {"host": "packages.microsoft.com", "port": 443, "description": "Microsoft packages"},
        {"host": "archive.ubuntu.com", "port": 80, "description": "Ubuntu packages"},
        {"host": "aka.ms", "port": 443, "description": "Microsoft redirects"},
    ]

# Custom Private Link endpoints (serverless to your VNet)
if 'PRIVATE_LINK_ENDPOINTS' not in globals():
    PRIVATE_LINK_ENDPOINTS = [
        {"host": "api.yourdomain.com", "port": 443, "description": "Internal API"},
    ]

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

def test_connectivity(host: str, port: int, description: str, timeout: int = 5) -> Dict:
    """Test connectivity to a host:port"""
    print_info(f"Testing: {description} ({host}:{port})", indent=1)
    
    result = {
        "host": host,
        "port": port,
        "description": description,
    }
    
    # DNS resolution
    try:
        start = time.time()
        ip = socket.gethostbyname(host)
        dns_time = time.time() - start
        
        result["ip"] = ip
        result["is_private"] = is_private_ip(ip)
        result["dns_time"] = dns_time
        
        print(f"    IP: {ip} ({'Private' if result['is_private'] else 'Public'})", indent=1)
        
    except Exception as e:
        result["dns_error"] = str(e)
        print_error(f"DNS failed: {e}", indent=2)
        return result
    
    # TCP connectivity
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start = time.time()
        sock.connect((host, port))
        connect_time = time.time() - start
        sock.close()
        
        result["tcp_time"] = connect_time
        result["status"] = "success"
        print_success(f"Connected in {connect_time:.3f}s", indent=2)
        
    except socket.timeout:
        result["status"] = "timeout"
        result["tcp_error"] = "Connection timeout"
        print_error("Connection timeout", indent=2)
    except Exception as e:
        result["status"] = "failed"
        result["tcp_error"] = str(e)
        print_error(f"Connection failed: {e}", indent=2)
    
    return result

def check_compute_type():
    """Check if running on serverless compute"""
    try:
        spark_conf = spark.conf.get("spark.databricks.clusterUsageTags.sparkVersion")
        print_info(f"Spark version: {spark_conf}")
        
        # Try to detect serverless
        cluster_type = spark.conf.get("spark.databricks.clusterUsageTags.clusterType", "unknown")
        print_info(f"Cluster type: {cluster_type}")
        
        if "serverless" in cluster_type.lower():
            print_success("Running on Serverless compute")
            return True
        else:
            print_warning("May not be running on serverless compute")
            print("   Results may not reflect serverless networking", indent=1)
            return False
    except:
        print_warning("Could not determine compute type")
        return None

def main():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Azure Databricks - Serverless Compute Diagnostics                  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check compute type
    print_header("Compute Environment")
    is_serverless = check_compute_type()
    
    all_results = []
    
    # Test 1: Storage Account Connectivity
    print_header("Storage Account Connectivity")
    
    for storage in STORAGE_ACCOUNTS:
        storage_name = storage["name"]
        
        if storage.get("test_adls", True):
            result = test_connectivity(
                f"{storage_name}.dfs.core.windows.net",
                443,
                f"ADLS Gen2 - {storage_name}"
            )
            all_results.append(result)
        
        if storage.get("test_blob", True):
            result = test_connectivity(
                f"{storage_name}.blob.core.windows.net",
                443,
                f"Blob Storage - {storage_name}"
            )
            all_results.append(result)
    
    # Test 2: External Service Connectivity (Egress)
    print_header("External Connectivity (Egress Validation)")
    print_info("Testing if serverless can reach external services...")
    
    for service in EXTERNAL_SERVICES:
        result = test_connectivity(
            service["host"],
            service["port"],
            service["description"]
        )
        all_results.append(result)
    
    # Test 3: Private Link Endpoints
    if PRIVATE_LINK_ENDPOINTS:
        print_header("Private Link to Internal Resources")
        print_info("Testing serverless Private Link to your VNet...")
        
        for endpoint in PRIVATE_LINK_ENDPOINTS:
            result = test_connectivity(
                endpoint["host"],
                endpoint["port"],
                endpoint["description"]
            )
            all_results.append(result)
    
    # Test 4: Egress IP Detection
    print_header("Egress IP Detection")
    print_info("Detecting serverless egress IP...")
    
    try:
        import requests
        egress_ip = requests.get("https://api.ipify.org", timeout=5).text
        print_success(f"Egress IP: {egress_ip}", indent=1)
        
        if is_private_ip(egress_ip):
            print_success("Egress via private IP (NAT)", indent=2)
        else:
            print_info("Egress via public IP", indent=2)
        
        all_results.append({
            "test": "egress_ip",
            "ip": egress_ip,
            "is_private": is_private_ip(egress_ip)
        })
    except Exception as e:
        print_error(f"Could not detect egress IP: {e}", indent=1)
    
    # Summary
    print_header("Summary")
    
    success = sum(1 for r in all_results if r.get("status") == "success")
    failed = sum(1 for r in all_results if r.get("status") in ["failed", "timeout"])
    blocked = sum(1 for r in all_results if "dns_error" in r or "tcp_error" in r)
    
    print(f"Total tests: {len(all_results)}")
    print(f"Successful: {Colors.GREEN}{success}{Colors.RESET}")
    print(f"Failed/Blocked: {Colors.RED}{blocked}{Colors.RESET}")
    
    # Key findings
    print_header("Key Findings")
    
    # Storage connectivity
    storage_results = [r for r in all_results if any(s["name"] in r.get("host", "") for s in STORAGE_ACCOUNTS)]
    if storage_results:
        storage_private = sum(1 for r in storage_results if r.get("is_private", False))
        if storage_private > 0:
            print_success(f"Storage uses Private Endpoints ({storage_private}/{len(storage_results)})")
        else:
            print_info("Storage uses public endpoints")
    
    # External connectivity
    external_results = [r for r in all_results if any(s["host"] == r.get("host") for s in EXTERNAL_SERVICES)]
    if external_results:
        external_success = sum(1 for r in external_results if r.get("status") == "success")
        external_blocked = sum(1 for r in external_results if r.get("status") in ["failed", "timeout"])
        
        if external_blocked > 0:
            print_warning(f"External access blocked: {external_blocked}/{len(external_results)} services")
            print("   Possible causes:", indent=1)
            print("   • Network policies restricting egress", indent=1)
            print("   • Firewall rules", indent=1)
            print("   • Service-specific blocks", indent=1)
        else:
            print_success("All external services reachable")
    
    # Private Link
    if PRIVATE_LINK_ENDPOINTS:
        pl_results = [r for r in all_results if any(e["host"] == r.get("host") for e in PRIVATE_LINK_ENDPOINTS)]
        pl_success = [r for r in pl_results if r.get("status") == "success" and r.get("is_private")]
        
        if len(pl_success) == len(pl_results):
            print_success("Private Link to internal resources working")
        elif pl_success:
            print_warning(f"Private Link partial: {len(pl_success)}/{len(pl_results)} working")
        else:
            print_error("Private Link not working")
    
    # Export JSON
    print_header("Detailed Results (JSON)")
    print(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "test": "serverless_diagnostics",
        "is_serverless": is_serverless,
        "summary": {
            "total": len(all_results),
            "success": success,
            "failed": blocked
        },
        "results": all_results
    }, indent=2))
    
    print(f"\n{Colors.BOLD}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
