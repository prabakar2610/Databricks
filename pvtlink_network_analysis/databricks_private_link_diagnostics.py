"""
Azure Databricks Private Link Connectivity Diagnostics
=======================================================
This script helps diagnose Private Link connectivity issues where DNS resolves 
to public IPs instead of private IPs.

Usage:
1. Copy this entire script into a Databricks notebook cell
2. Update the CONFIGURATION section with your values
3. Run the cell
4. Review the diagnostic output

Author: Troubleshooting Guide for Azure Private Link Issues
"""

import socket
import time
import json
from typing import Tuple, Dict, List
from datetime import datetime

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# List of domains/services you're trying to reach
DOMAINS_TO_TEST = [
    {"host": "api.internal.yourdomain.com", "port": 443},
    {"host": "api.internal.yourdomain.com", "port": 80},
    # Add more domains as needed:
    # {"host": "your-service.your-domain.com", "port": 8080},
]

# Your Private DNS Zone name (as configured in Azure)
PRIVATE_DNS_ZONE = "internal.yourdomain.com"

# Domain configured in NCC (Databricks Network Connectivity Config)
NCC_DOMAIN = "internal.yourdomain.com"

# Expected private IP range (first 2 octets, e.g., "10.0" for 10.0.x.x)
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

# ============================================================================
# DO NOT MODIFY BELOW THIS LINE
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text: str):
    """Print a formatted section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
    print(f" {text}")
    print(f"{'='*80}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def is_private_ip(ip: str) -> bool:
    """Check if an IP address is in private range"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        first = int(parts[0])
        second = int(parts[1])
        
        # Check standard private ranges
        if first == 10:
            return True
        if first == 172 and 16 <= second <= 31:
            return True
        if first == 192 and second == 168:
            return True
        if first == 127:  # Loopback
            return True
        
        return False
    except:
        return False

def check_expected_private_range(ip: str, expected_prefix: str) -> bool:
    """Check if IP matches expected private range"""
    if not expected_prefix:
        return True
    return ip.startswith(expected_prefix)

def resolve_dns(hostname: str) -> Tuple[bool, str, str]:
    """
    Resolve DNS and check if it's private
    Returns: (success, ip_address, message)
    """
    try:
        start_time = time.time()
        ip_address = socket.gethostbyname(hostname)
        elapsed = time.time() - start_time
        
        message = f"Resolved in {elapsed:.3f}s to {ip_address}"
        return True, ip_address, message
    except socket.gaierror as e:
        return False, "", f"DNS resolution failed: {e}"
    except Exception as e:
        return False, "", f"Unexpected error: {e}"

def test_tcp_connection(hostname: str, port: int, timeout: int = 5) -> Tuple[bool, str, float]:
    """
    Test TCP connection to a host:port
    Returns: (success, message, elapsed_time)
    """
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((hostname, port))
        elapsed = time.time() - start_time
        
        sock.close()
        
        if result == 0:
            return True, "Connection successful", elapsed
        else:
            return False, f"Connection refused (error code: {result})", elapsed
            
    except socket.timeout:
        elapsed = time.time() - start_time
        return False, f"Connection timeout after {timeout}s", elapsed
    except socket.gaierror as e:
        elapsed = time.time() - start_time
        return False, f"DNS resolution failed: {e}", elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        return False, f"Connection error: {e}", elapsed

def get_egress_ip() -> Tuple[bool, str]:
    """
    Get the egress IP to check if NCC is being used
    Returns: (success, ip_or_error)
    """
    try:
        import requests
        response = requests.get("https://ifconfig.me", timeout=10)
        return True, response.text.strip()
    except Exception as e:
        return False, f"Failed to get egress IP: {e}"

def test_multiple_dns_servers(hostname: str) -> Dict[str, str]:
    """
    Test DNS resolution (basic socket resolution)
    """
    results = {}
    
    # Default system DNS
    try:
        ip = socket.gethostbyname(hostname)
        results['system_dns'] = ip
    except Exception as e:
        results['system_dns'] = f"Error: {e}"
    
    return results

def run_comprehensive_test(domain_config: Dict) -> Dict:
    """
    Run comprehensive connectivity test for a single domain
    Returns dictionary with all test results
    """
    hostname = domain_config['host']
    port = domain_config['port']
    
    results = {
        'hostname': hostname,
        'port': port,
        'timestamp': datetime.now().isoformat(),
        'dns_resolution': {},
        'tcp_connection': {},
        'overall_status': 'UNKNOWN'
    }
    
    # Step 1: DNS Resolution
    dns_success, ip_address, dns_message = resolve_dns(hostname)
    results['dns_resolution'] = {
        'success': dns_success,
        'ip_address': ip_address,
        'message': dns_message,
        'is_private': is_private_ip(ip_address) if dns_success else False,
        'matches_expected_range': check_expected_private_range(ip_address, EXPECTED_PRIVATE_IP_PREFIX) if dns_success else False
    }
    
    # Step 2: TCP Connection (only if DNS succeeded)
    if dns_success:
        tcp_success, tcp_message, elapsed = test_tcp_connection(hostname, port)
        results['tcp_connection'] = {
            'success': tcp_success,
            'message': tcp_message,
            'elapsed_time': elapsed
        }
    else:
        results['tcp_connection'] = {
            'success': False,
            'message': 'Skipped due to DNS failure',
            'elapsed_time': 0
        }
    
    # Determine overall status
    if not dns_success:
        results['overall_status'] = 'DNS_FAILURE'
    elif not results['dns_resolution']['is_private']:
        results['overall_status'] = 'PUBLIC_IP_RESOLVED'
    elif not results['dns_resolution']['matches_expected_range']:
        results['overall_status'] = 'WRONG_PRIVATE_RANGE'
    elif not results['tcp_connection']['success']:
        results['overall_status'] = 'TCP_FAILURE'
    else:
        results['overall_status'] = 'SUCCESS'
    
    return results

def print_test_results(results: Dict):
    """Print formatted test results"""
    hostname = results['hostname']
    port = results['port']
    status = results['overall_status']
    
    print(f"\n{Colors.BOLD}Testing: {hostname}:{port}{Colors.RESET}")
    print(f"{'-'*80}")
    
    # DNS Results
    dns = results['dns_resolution']
    if dns['success']:
        print_success(f"DNS Resolution: {dns['ip_address']} ({dns['message']})")
        
        if dns['is_private']:
            if dns['matches_expected_range']:
                print_success(f"IP Type: Private IP (matches expected range {EXPECTED_PRIVATE_IP_PREFIX}.x.x)")
            else:
                print_warning(f"IP Type: Private IP (but doesn't match expected range {EXPECTED_PRIVATE_IP_PREFIX}.x.x)")
        else:
            print_error(f"IP Type: PUBLIC IP - Private Link is NOT being used!")
    else:
        print_error(f"DNS Resolution: {dns['message']}")
    
    # TCP Results
    tcp = results['tcp_connection']
    if tcp['message'] != 'Skipped due to DNS failure':
        if tcp['success']:
            print_success(f"TCP Connection: {tcp['message']} ({tcp['elapsed_time']:.3f}s)")
        else:
            print_error(f"TCP Connection: {tcp['message']} ({tcp['elapsed_time']:.3f}s)")
    
    # Overall Status
    print(f"\n{Colors.BOLD}Overall Status:{Colors.RESET} ", end="")
    if status == 'SUCCESS':
        print_success("ALL TESTS PASSED ✓")
    elif status == 'PUBLIC_IP_RESOLVED':
        print_error("PRIVATE LINK NOT WORKING - DNS resolves to PUBLIC IP")
    elif status == 'DNS_FAILURE':
        print_error("DNS RESOLUTION FAILED")
    elif status == 'WRONG_PRIVATE_RANGE':
        print_warning("DNS resolves to private IP but wrong range")
    elif status == 'TCP_FAILURE':
        print_error("DNS OK but TCP CONNECTION FAILED")
    else:
        print_warning("UNKNOWN STATUS")

def print_configuration_check():
    """Print configuration validation"""
    print_header("Configuration Validation")
    
    print(f"{Colors.BOLD}Your Configuration:{Colors.RESET}")
    print(f"  Private DNS Zone:     {PRIVATE_DNS_ZONE}")
    print(f"  NCC Domain:           {NCC_DOMAIN}")
    print(f"  Expected IP Prefix:   {EXPECTED_PRIVATE_IP_PREFIX}.x.x")
    print(f"  Domains to test:      {len(DOMAINS_TO_TEST)}")
    
    # Check if Private DNS Zone matches NCC Domain
    if PRIVATE_DNS_ZONE == NCC_DOMAIN:
        print_success("Private DNS Zone matches NCC Domain ✓")
    else:
        print_error("MISMATCH: Private DNS Zone and NCC Domain should match!")
        print(f"  Private DNS Zone: {PRIVATE_DNS_ZONE}")
        print(f"  NCC Domain:       {NCC_DOMAIN}")
    
    # Check domain configuration
    print(f"\n{Colors.BOLD}Domains to test:{Colors.RESET}")
    for i, domain in enumerate(DOMAINS_TO_TEST, 1):
        print(f"  {i}. {domain['host']}:{domain['port']}")
        
        # Check if hostname matches the DNS zone
        if domain['host'].endswith(PRIVATE_DNS_ZONE):
            print(f"     {Colors.GREEN}✓ Hostname matches DNS zone{Colors.RESET}")
        else:
            print(f"     {Colors.YELLOW}⚠️  Hostname doesn't match DNS zone suffix{Colors.RESET}")

def print_diagnostics_summary(all_results: List[Dict], egress_ip: str):
    """Print summary of all diagnostics"""
    print_header("Diagnostic Summary")
    
    success_count = sum(1 for r in all_results if r['overall_status'] == 'SUCCESS')
    public_ip_count = sum(1 for r in all_results if r['overall_status'] == 'PUBLIC_IP_RESOLVED')
    dns_failure_count = sum(1 for r in all_results if r['overall_status'] == 'DNS_FAILURE')
    tcp_failure_count = sum(1 for r in all_results if r['overall_status'] == 'TCP_FAILURE')
    
    print(f"{Colors.BOLD}Test Results:{Colors.RESET}")
    print(f"  Total tests:          {len(all_results)}")
    print(f"  {Colors.GREEN}Successful:           {success_count}{Colors.RESET}")
    print(f"  {Colors.RED}Public IP resolved:   {public_ip_count}{Colors.RESET}")
    print(f"  {Colors.RED}DNS failures:         {dns_failure_count}{Colors.RESET}")
    print(f"  {Colors.RED}TCP failures:         {tcp_failure_count}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Egress IP Check:{Colors.RESET}")
    print(f"  Your egress IP: {egress_ip}")
    if is_private_ip(egress_ip):
        print_success("Egress IP is private - may indicate NCC is active")
    else:
        print_warning("Egress IP is public - NCC may not be applied to this workspace")
    
    # Provide recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.RESET}")
    
    if public_ip_count > 0:
        print_error("\n🔍 CRITICAL ISSUE: DNS resolving to PUBLIC IP")
        print("   This means Private Link is NOT being used. Check:")
        print("   1. Private DNS Zone name exactly matches NCC Domain")
        print("   2. Private DNS Zone is linked to the VNet with Private Endpoint")
        print("   3. A record in Private DNS Zone points to Load Balancer private IP")
        print("   4. NCC Domain field has ONLY the zone name (no protocol, hostname, wildcards)")
        print("   5. Workspace is actually attached to and using this NCC")
        print("   6. Private Endpoint status is 'Established' in NCC")
    
    if dns_failure_count > 0:
        print_error("\n🔍 DNS Resolution Failures Detected")
        print("   Possible causes:")
        print("   1. Domain name doesn't exist in Private DNS Zone")
        print("   2. Private DNS Zone not properly configured")
        print("   3. Typo in domain name")
    
    if tcp_failure_count > 0 and public_ip_count == 0:
        print_error("\n🔍 TCP Connection Failures (but DNS is private)")
        print("   Private Link DNS is working, but connectivity fails. Check:")
        print("   1. Load Balancer health probe status")
        print("   2. Backend pool configuration")
        print("   3. NSG rules allowing traffic from Private Endpoint subnet")
        print("   4. Backend service is actually listening on the port")
        print("   5. Azure Firewall rules (if applicable)")
    
    if success_count == len(all_results) and len(all_results) > 0:
        print_success("\n🎉 All tests passed! Private Link is working correctly.")

def main():
    """Main execution function"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║     Azure Databricks Private Link Connectivity Diagnostics                ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Configuration Check
    print_configuration_check()
    
    # Step 2: Get Egress IP
    print_header("Network Egress Check")
    print_info("Checking egress IP to verify if NCC is active...")
    egress_success, egress_ip = get_egress_ip()
    if egress_success:
        print_success(f"Egress IP: {egress_ip}")
    else:
        print_warning(f"Could not determine egress IP: {egress_ip}")
        egress_ip = "Unknown"
    
    # Step 3: Run Connectivity Tests
    print_header("Connectivity Tests")
    
    all_results = []
    for domain_config in DOMAINS_TO_TEST:
        results = run_comprehensive_test(domain_config)
        all_results.append(results)
        print_test_results(results)
    
    # Step 4: Summary
    print_diagnostics_summary(all_results, egress_ip)
    
    # Step 5: Export results as JSON for further analysis
    print_header("Detailed Results (JSON)")
    print_info("Copy the JSON below for detailed analysis or support tickets:")
    print(f"\n{Colors.CYAN}{json.dumps({
        'test_timestamp': datetime.now().isoformat(),
        'configuration': {
            'private_dns_zone': PRIVATE_DNS_ZONE,
            'ncc_domain': NCC_DOMAIN,
            'expected_ip_prefix': EXPECTED_PRIVATE_IP_PREFIX
        },
        'egress_ip': egress_ip,
        'test_results': all_results
    }, indent=2)}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

# ============================================================================
# RUN THE DIAGNOSTICS
# ============================================================================

if __name__ == "__main__":
    main()
