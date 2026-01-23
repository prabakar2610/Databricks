"""
Azure Databricks Private Link Connectivity Diagnostics - ENHANCED VERSION
===========================================================================
This enhanced script provides comprehensive network diagnostics for Private Link issues.

Features:
- Advanced DNS diagnostics with multiple resolution attempts
- Port scanning and service detection
- Network latency and performance analysis
- Detailed timing breakdowns
- Comparative analysis across multiple domains
- Advanced error detection and root cause analysis

Usage:
1. Copy this entire script into a Databricks notebook cell
2. Update the CONFIGURATION section with your values
3. Run the cell
4. Review the comprehensive diagnostic output

Author: Enhanced Troubleshooting Guide for Azure Private Link Issues
Version: 2.0
"""

import socket
import time
import json
import sys
from typing import Tuple, Dict, List, Optional
from datetime import datetime
import threading
from collections import defaultdict

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# List of domains/services you're trying to reach
DOMAINS_TO_TEST = [
    {"host": "api.internal.yourdomain.com", "port": 443, "description": "API Service HTTPS"},
    {"host": "api.internal.yourdomain.com", "port": 80, "description": "API Service HTTP"},
    # Add more domains as needed:
    # {"host": "db.internal.yourdomain.com", "port": 5432, "description": "PostgreSQL Database"},
    # {"host": "app.internal.yourdomain.com", "port": 8080, "description": "Application Server"},
]

# Your Private DNS Zone name (as configured in Azure)
PRIVATE_DNS_ZONE = "internal.yourdomain.com"

# Domain configured in NCC (Databricks Network Connectivity Config)
NCC_DOMAIN = "internal.yourdomain.com"

# Expected private IP range (first 2 octets, e.g., "10.0" for 10.0.x.x)
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

# Expected Load Balancer frontend private IP (if known)
EXPECTED_LB_PRIVATE_IP = "10.0.1.100"  # Set to None if unknown

# Number of DNS resolution attempts for reliability testing
DNS_RETRY_COUNT = 5

# Number of TCP connection attempts for reliability testing
TCP_RETRY_COUNT = 3

# Connection timeout in seconds
CONNECTION_TIMEOUT = 5

# Additional ports to scan for each host (common ports)
ADDITIONAL_PORTS_TO_SCAN = [80, 443, 8080, 8443, 3306, 5432, 27017]

# Enable/disable additional diagnostics
ENABLE_PORT_SCANNING = True
ENABLE_MULTIPLE_RESOLUTION_TESTS = True
ENABLE_LATENCY_ANALYSIS = True
ENABLE_EXTERNAL_CONNECTIVITY_TEST = True

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
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def print_header(text: str, level: int = 1):
    """Print a formatted section header"""
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

def is_private_ip(ip: str) -> bool:
    """Check if an IP address is in private range"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        first = int(parts[0])
        second = int(parts[1])
        
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

def get_ip_info(ip: str) -> Dict:
    """Get detailed information about an IP address"""
    info = {
        'ip': ip,
        'is_private': is_private_ip(ip),
        'ip_class': 'Unknown',
        'range_type': 'Unknown'
    }
    
    try:
        parts = [int(p) for p in ip.split('.')]
        first = parts[0]
        second = parts[1]
        
        # Determine IP class
        if 1 <= first <= 126:
            info['ip_class'] = 'Class A'
        elif 128 <= first <= 191:
            info['ip_class'] = 'Class B'
        elif 192 <= first <= 223:
            info['ip_class'] = 'Class C'
        elif 224 <= first <= 239:
            info['ip_class'] = 'Class D (Multicast)'
        elif 240 <= first <= 255:
            info['ip_class'] = 'Class E (Reserved)'
        
        # Determine range type
        if first == 10:
            info['range_type'] = 'Private (10.0.0.0/8)'
        elif first == 172 and 16 <= second <= 31:
            info['range_type'] = 'Private (172.16.0.0/12)'
        elif first == 192 and second == 168:
            info['range_type'] = 'Private (192.168.0.0/16)'
        elif first == 127:
            info['range_type'] = 'Loopback (127.0.0.0/8)'
        elif first == 169 and second == 254:
            info['range_type'] = 'Link-Local (169.254.0.0/16)'
        else:
            info['range_type'] = 'Public/Routable'
        
    except:
        pass
    
    return info

def resolve_dns_multiple_times(hostname: str, attempts: int = 5) -> Dict:
    """
    Resolve DNS multiple times to check consistency
    Returns statistics about resolution
    """
    results = {
        'hostname': hostname,
        'attempts': attempts,
        'successful_attempts': 0,
        'failed_attempts': 0,
        'unique_ips': set(),
        'resolution_times': [],
        'errors': [],
        'is_consistent': False,
        'average_time': 0,
        'min_time': 0,
        'max_time': 0
    }
    
    for i in range(attempts):
        try:
            start_time = time.time()
            ip = socket.gethostbyname(hostname)
            elapsed = time.time() - start_time
            
            results['successful_attempts'] += 1
            results['unique_ips'].add(ip)
            results['resolution_times'].append(elapsed)
        except Exception as e:
            results['failed_attempts'] += 1
            results['errors'].append(str(e))
        
        # Small delay between attempts
        if i < attempts - 1:
            time.sleep(0.1)
    
    # Calculate statistics
    if results['resolution_times']:
        results['average_time'] = sum(results['resolution_times']) / len(results['resolution_times'])
        results['min_time'] = min(results['resolution_times'])
        results['max_time'] = max(results['resolution_times'])
    
    results['is_consistent'] = len(results['unique_ips']) <= 1
    results['unique_ips'] = list(results['unique_ips'])
    
    return results

def test_tcp_connection_advanced(hostname: str, port: int, timeout: int = 5) -> Dict:
    """
    Advanced TCP connection test with detailed metrics
    """
    result = {
        'hostname': hostname,
        'port': port,
        'success': False,
        'error': None,
        'timings': {
            'dns_lookup': 0,
            'tcp_connection': 0,
            'total': 0
        },
        'resolved_ip': None
    }
    
    try:
        total_start = time.time()
        
        # DNS lookup
        dns_start = time.time()
        ip = socket.gethostbyname(hostname)
        result['timings']['dns_lookup'] = time.time() - dns_start
        result['resolved_ip'] = ip
        
        # TCP connection
        tcp_start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        result['timings']['tcp_connection'] = time.time() - tcp_start
        sock.close()
        
        result['timings']['total'] = time.time() - total_start
        result['success'] = True
        
    except socket.timeout:
        result['error'] = 'Connection timeout'
        result['timings']['total'] = time.time() - total_start
    except socket.gaierror as e:
        result['error'] = f'DNS error: {e}'
        result['timings']['total'] = time.time() - total_start
    except ConnectionRefusedError:
        result['error'] = 'Connection refused'
        result['timings']['total'] = time.time() - total_start
    except Exception as e:
        result['error'] = str(e)
        result['timings']['total'] = time.time() - total_start
    
    return result

def scan_ports(hostname: str, ports: List[int], timeout: int = 2) -> Dict:
    """
    Scan multiple ports to identify open services
    """
    results = {
        'hostname': hostname,
        'total_ports': len(ports),
        'open_ports': [],
        'closed_ports': [],
        'filtered_ports': [],
        'scan_duration': 0
    }
    
    start_time = time.time()
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((hostname, port))
            sock.close()
            
            if result == 0:
                results['open_ports'].append(port)
            else:
                results['closed_ports'].append(port)
        except socket.timeout:
            results['filtered_ports'].append(port)
        except:
            results['filtered_ports'].append(port)
    
    results['scan_duration'] = time.time() - start_time
    return results

def get_socket_info() -> Dict:
    """Get information about socket configuration"""
    info = {
        'default_timeout': socket.getdefaulttimeout(),
        'hostname': socket.gethostname(),
        'fqdn': socket.getfqdn(),
    }
    
    try:
        info['local_ip'] = socket.gethostbyname(socket.gethostname())
    except:
        info['local_ip'] = 'Unable to determine'
    
    return info

def test_external_connectivity() -> Dict:
    """Test connectivity to external services to verify general network access"""
    external_services = [
        {'host': 'www.google.com', 'port': 443, 'name': 'Google'},
        {'host': 'www.microsoft.com', 'port': 443, 'name': 'Microsoft'},
        {'host': '8.8.8.8', 'port': 53, 'name': 'Google DNS'},
    ]
    
    results = {
        'total_tested': len(external_services),
        'successful': 0,
        'failed': 0,
        'details': []
    }
    
    for service in external_services:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            start = time.time()
            sock.connect((service['host'], service['port']))
            elapsed = time.time() - start
            sock.close()
            
            results['successful'] += 1
            results['details'].append({
                'name': service['name'],
                'host': service['host'],
                'port': service['port'],
                'status': 'success',
                'time': elapsed
            })
        except Exception as e:
            results['failed'] += 1
            results['details'].append({
                'name': service['name'],
                'host': service['host'],
                'port': service['port'],
                'status': 'failed',
                'error': str(e)
            })
    
    return results

def get_egress_ip_detailed() -> Dict:
    """Get detailed egress IP information"""
    result = {
        'success': False,
        'ip': None,
        'is_private': False,
        'services_tested': []
    }
    
    # Try multiple services
    services = [
        'https://ifconfig.me',
        'https://api.ipify.org',
        'https://icanhazip.com'
    ]
    
    for service_url in services:
        try:
            import requests
            response = requests.get(service_url, timeout=5)
            ip = response.text.strip()
            
            result['services_tested'].append({
                'service': service_url,
                'status': 'success',
                'ip': ip
            })
            
            if not result['success']:
                result['success'] = True
                result['ip'] = ip
                result['is_private'] = is_private_ip(ip)
            
        except Exception as e:
            result['services_tested'].append({
                'service': service_url,
                'status': 'failed',
                'error': str(e)
            })
    
    return result

def analyze_dns_pattern(domains: List[Dict]) -> Dict:
    """Analyze DNS resolution patterns across multiple domains"""
    analysis = {
        'total_domains': len(domains),
        'all_resolve_to_same_ip': False,
        'common_ip': None,
        'ip_distribution': defaultdict(int),
        'all_private': True,
        'all_public': True,
        'mixed': False
    }
    
    ips = []
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain['host'])
            ips.append(ip)
            analysis['ip_distribution'][ip] += 1
            
            if is_private_ip(ip):
                analysis['all_public'] = False
            else:
                analysis['all_private'] = False
        except:
            pass
    
    if ips:
        unique_ips = set(ips)
        if len(unique_ips) == 1:
            analysis['all_resolve_to_same_ip'] = True
            analysis['common_ip'] = list(unique_ips)[0]
        
        analysis['mixed'] = not analysis['all_private'] and not analysis['all_public']
    
    return analysis

def run_comprehensive_diagnostics(domain_config: Dict) -> Dict:
    """Run comprehensive diagnostics for a single domain"""
    hostname = domain_config['host']
    port = domain_config['port']
    description = domain_config.get('description', 'N/A')
    
    print_header(f"Testing: {hostname}:{port} - {description}", level=3)
    
    results = {
        'hostname': hostname,
        'port': port,
        'description': description,
        'timestamp': datetime.now().isoformat(),
        'dns_resolution': {},
        'dns_reliability': {},
        'ip_details': {},
        'tcp_connection': {},
        'tcp_reliability': {},
        'port_scan': {},
        'overall_status': 'UNKNOWN',
        'issues_found': []
    }
    
    # Test 1: Single DNS Resolution
    print_info("DNS Resolution Test...", indent=1)
    try:
        start = time.time()
        ip = socket.gethostbyname(hostname)
        elapsed = time.time() - start
        
        results['dns_resolution'] = {
            'success': True,
            'ip': ip,
            'time': elapsed
        }
        
        print_success(f"Resolved to {ip} in {elapsed:.3f}s", indent=2)
        
        # Get IP details
        ip_info = get_ip_info(ip)
        results['ip_details'] = ip_info
        
        if ip_info['is_private']:
            print_success(f"IP is {ip_info['range_type']}", indent=2)
        else:
            print_error(f"IP is {ip_info['range_type']} - Private Link NOT in use!", indent=2)
            results['issues_found'].append('DNS resolves to public IP')
        
        # Check if matches expected
        if EXPECTED_LB_PRIVATE_IP and ip != EXPECTED_LB_PRIVATE_IP:
            print_warning(f"IP doesn't match expected LB IP: {EXPECTED_LB_PRIVATE_IP}", indent=2)
            results['issues_found'].append(f'IP mismatch: got {ip}, expected {EXPECTED_LB_PRIVATE_IP}')
        
    except Exception as e:
        results['dns_resolution'] = {
            'success': False,
            'error': str(e)
        }
        print_error(f"DNS resolution failed: {e}", indent=2)
        results['issues_found'].append(f'DNS resolution failed: {e}')
    
    # Test 2: Multiple DNS Resolutions (Reliability)
    if ENABLE_MULTIPLE_RESOLUTION_TESTS and results['dns_resolution'].get('success'):
        print_info(f"DNS Reliability Test ({DNS_RETRY_COUNT} attempts)...", indent=1)
        dns_stats = resolve_dns_multiple_times(hostname, DNS_RETRY_COUNT)
        results['dns_reliability'] = dns_stats
        
        if dns_stats['successful_attempts'] == DNS_RETRY_COUNT:
            print_success(f"All {DNS_RETRY_COUNT} resolutions successful", indent=2)
        else:
            print_warning(f"{dns_stats['failed_attempts']}/{DNS_RETRY_COUNT} resolutions failed", indent=2)
        
        if dns_stats['is_consistent']:
            print_success(f"DNS is consistent (always resolves to same IP)", indent=2)
        else:
            print_warning(f"DNS is inconsistent - resolved to {len(dns_stats['unique_ips'])} different IPs: {dns_stats['unique_ips']}", indent=2)
            results['issues_found'].append('Inconsistent DNS resolution')
        
        print_metric(f"Avg resolution time", f"{dns_stats['average_time']:.3f}s", indent=2)
        print_metric(f"Min/Max time", f"{dns_stats['min_time']:.3f}s / {dns_stats['max_time']:.3f}s", indent=2)
    
    # Test 3: TCP Connection
    if results['dns_resolution'].get('success'):
        print_info("TCP Connection Test...", indent=1)
        tcp_result = test_tcp_connection_advanced(hostname, port, CONNECTION_TIMEOUT)
        results['tcp_connection'] = tcp_result
        
        if tcp_result['success']:
            print_success(f"Connection successful", indent=2)
            print_metric("DNS lookup time", f"{tcp_result['timings']['dns_lookup']:.3f}s", indent=2)
            print_metric("TCP connect time", f"{tcp_result['timings']['tcp_connection']:.3f}s", indent=2)
            print_metric("Total time", f"{tcp_result['timings']['total']:.3f}s", indent=2)
        else:
            print_error(f"Connection failed: {tcp_result['error']}", indent=2)
            results['issues_found'].append(f'TCP connection failed: {tcp_result["error"]}')
        
        # Test 4: TCP Reliability
        if tcp_result['success'] and TCP_RETRY_COUNT > 1:
            print_info(f"TCP Reliability Test ({TCP_RETRY_COUNT} attempts)...", indent=1)
            tcp_times = []
            tcp_failures = 0
            
            for i in range(TCP_RETRY_COUNT):
                retry_result = test_tcp_connection_advanced(hostname, port, CONNECTION_TIMEOUT)
                if retry_result['success']:
                    tcp_times.append(retry_result['timings']['total'])
                else:
                    tcp_failures += 1
            
            results['tcp_reliability'] = {
                'attempts': TCP_RETRY_COUNT,
                'successful': TCP_RETRY_COUNT - tcp_failures,
                'failed': tcp_failures,
                'times': tcp_times,
                'avg_time': sum(tcp_times) / len(tcp_times) if tcp_times else 0
            }
            
            if tcp_failures == 0:
                print_success(f"All {TCP_RETRY_COUNT} connections successful", indent=2)
                print_metric("Avg connection time", f"{results['tcp_reliability']['avg_time']:.3f}s", indent=2)
            else:
                print_warning(f"{tcp_failures}/{TCP_RETRY_COUNT} connections failed", indent=2)
                results['issues_found'].append('Unreliable TCP connection')
    
    # Test 5: Port Scanning
    if ENABLE_PORT_SCANNING and results['dns_resolution'].get('success'):
        print_info("Port Scan (Common Ports)...", indent=1)
        scan_results = scan_ports(hostname, ADDITIONAL_PORTS_TO_SCAN, timeout=2)
        results['port_scan'] = scan_results
        
        if scan_results['open_ports']:
            print_success(f"Open ports found: {scan_results['open_ports']}", indent=2)
        else:
            print_warning("No common ports found open", indent=2)
        
        print_metric("Scan duration", f"{scan_results['scan_duration']:.2f}s", indent=2)
    
    # Determine overall status
    if not results['dns_resolution'].get('success'):
        results['overall_status'] = 'DNS_FAILURE'
    elif not results['ip_details'].get('is_private'):
        results['overall_status'] = 'PUBLIC_IP_RESOLVED'
    elif not results['tcp_connection'].get('success'):
        results['overall_status'] = 'TCP_FAILURE'
    elif results['tcp_reliability'].get('failed', 0) > 0:
        results['overall_status'] = 'UNRELIABLE'
    else:
        results['overall_status'] = 'SUCCESS'
    
    # Print summary
    print(f"\n{Colors.BOLD}Result:{Colors.RESET} ", end="")
    if results['overall_status'] == 'SUCCESS':
        print_success("PASS ✓")
    elif results['overall_status'] == 'PUBLIC_IP_RESOLVED':
        print_error("FAIL - Private Link not working")
    elif results['overall_status'] == 'DNS_FAILURE':
        print_error("FAIL - DNS resolution failed")
    elif results['overall_status'] == 'TCP_FAILURE':
        print_error("FAIL - TCP connection failed")
    elif results['overall_status'] == 'UNRELIABLE':
        print_warning("PASS - But connection is unreliable")
    
    return results

def print_system_diagnostics():
    """Print system-level diagnostics"""
    print_header("System & Network Environment")
    
    # Socket info
    socket_info = get_socket_info()
    print_info("Socket Configuration:")
    print_metric("Hostname", socket_info['hostname'], indent=1)
    print_metric("FQDN", socket_info['fqdn'], indent=1)
    print_metric("Local IP", socket_info['local_ip'], indent=1)
    print_metric("Default timeout", f"{socket_info['default_timeout']}", indent=1)
    
    # Python environment
    print_info("\nPython Environment:")
    print_metric("Python version", sys.version.split()[0], indent=1)
    print_metric("Platform", sys.platform, indent=1)
    
    # External connectivity
    if ENABLE_EXTERNAL_CONNECTIVITY_TEST:
        print_info("\nExternal Connectivity Test:")
        ext_results = test_external_connectivity()
        
        if ext_results['successful'] == ext_results['total_tested']:
            print_success(f"All {ext_results['total_tested']} external services reachable", indent=1)
        else:
            print_warning(f"Only {ext_results['successful']}/{ext_results['total_tested']} external services reachable", indent=1)
        
        for detail in ext_results['details']:
            if detail['status'] == 'success':
                print_success(f"{detail['name']}: {detail['time']:.3f}s", indent=2)
            else:
                print_error(f"{detail['name']}: {detail['error']}", indent=2)
    
    # Egress IP
    print_info("\nEgress IP Detection:")
    egress_result = get_egress_ip_detailed()
    
    if egress_result['success']:
        print_success(f"Egress IP: {egress_result['ip']}", indent=1)
        if egress_result['is_private']:
            print_success("Egress IP is PRIVATE - NCC likely active", indent=2)
        else:
            print_warning("Egress IP is PUBLIC - NCC may not be active", indent=2)
    else:
        print_warning("Could not determine egress IP", indent=1)
    
    for service in egress_result['services_tested']:
        status = "✓" if service['status'] == 'success' else "✗"
        print(f"    {status} {service['service']}")

def print_configuration_validation():
    """Print configuration validation"""
    print_header("Configuration Validation")
    
    print(f"{Colors.BOLD}Your Configuration:{Colors.RESET}")
    print_metric("Private DNS Zone", PRIVATE_DNS_ZONE, indent=1)
    print_metric("NCC Domain", NCC_DOMAIN, indent=1)
    print_metric("Expected IP Prefix", f"{EXPECTED_PRIVATE_IP_PREFIX}.x.x", indent=1)
    
    if EXPECTED_LB_PRIVATE_IP:
        print_metric("Expected LB IP", EXPECTED_LB_PRIVATE_IP, indent=1)
    
    print_metric("Domains to test", len(DOMAINS_TO_TEST), indent=1)
    
    print(f"\n{Colors.BOLD}Validation Results:{Colors.RESET}")
    
    # Check DNS Zone matches NCC Domain
    if PRIVATE_DNS_ZONE == NCC_DOMAIN:
        print_success("Private DNS Zone matches NCC Domain ✓", indent=1)
    else:
        print_error("CRITICAL: Private DNS Zone and NCC Domain MISMATCH!", indent=1)
        print_error(f"  DNS Zone: {PRIVATE_DNS_ZONE}", indent=2)
        print_error(f"  NCC Domain: {NCC_DOMAIN}", indent=2)
        print_error("  These MUST match exactly for Private Link to work!", indent=2)
    
    # Check each domain
    print(f"\n{Colors.BOLD}Domains Configuration:{Colors.RESET}")
    for i, domain in enumerate(DOMAINS_TO_TEST, 1):
        print(f"  {i}. {domain['host']}:{domain['port']} - {domain.get('description', 'N/A')}")
        
        if domain['host'].endswith(PRIVATE_DNS_ZONE):
            print_success(f"Hostname matches DNS zone suffix ✓", indent=2)
        else:
            print_warning(f"Hostname doesn't match DNS zone suffix", indent=2)
            print_warning(f"  Domain ends with: {domain['host'].split('.')[-2:]}", indent=3)
            print_warning(f"  Expected zone: {PRIVATE_DNS_ZONE}", indent=3)

def print_comprehensive_summary(all_results: List[Dict], pattern_analysis: Dict):
    """Print comprehensive summary of all diagnostics"""
    print_header("Comprehensive Diagnostic Summary")
    
    # Count results
    success_count = sum(1 for r in all_results if r['overall_status'] == 'SUCCESS')
    public_ip_count = sum(1 for r in all_results if r['overall_status'] == 'PUBLIC_IP_RESOLVED')
    dns_failure_count = sum(1 for r in all_results if r['overall_status'] == 'DNS_FAILURE')
    tcp_failure_count = sum(1 for r in all_results if r['overall_status'] == 'TCP_FAILURE')
    unreliable_count = sum(1 for r in all_results if r['overall_status'] == 'UNRELIABLE')
    
    print(f"{Colors.BOLD}Test Results Summary:{Colors.RESET}")
    print_metric("Total tests", len(all_results), indent=1)
    print_metric("Successful", f"{success_count} {Colors.GREEN}✓{Colors.RESET}", indent=1)
    print_metric("Public IP resolved", f"{public_ip_count} {Colors.RED}✗{Colors.RESET}", indent=1)
    print_metric("DNS failures", f"{dns_failure_count} {Colors.RED}✗{Colors.RESET}", indent=1)
    print_metric("TCP failures", f"{tcp_failure_count} {Colors.RED}✗{Colors.RESET}", indent=1)
    print_metric("Unreliable", f"{unreliable_count} {Colors.YELLOW}⚠{Colors.RESET}", indent=1)
    
    # Pattern analysis
    print(f"\n{Colors.BOLD}DNS Pattern Analysis:{Colors.RESET}")
    if pattern_analysis['all_resolve_to_same_ip']:
        print_warning(f"All domains resolve to same IP: {pattern_analysis['common_ip']}", indent=1)
        print_warning("This may indicate NAT or a misconfiguration", indent=2)
    else:
        print_success("Domains resolve to different IPs (expected)", indent=1)
    
    if pattern_analysis['all_public']:
        print_error("ALL domains resolve to PUBLIC IPs - Private Link NOT working!", indent=1)
    elif pattern_analysis['all_private']:
        print_success("All domains resolve to PRIVATE IPs ✓", indent=1)
    elif pattern_analysis['mixed']:
        print_warning("Mixed public/private IPs - inconsistent configuration!", indent=1)
    
    # Detailed issues
    all_issues = []
    for result in all_results:
        if result['issues_found']:
            all_issues.extend(result['issues_found'])
    
    if all_issues:
        print(f"\n{Colors.BOLD}Issues Detected:{Colors.RESET}")
        unique_issues = list(set(all_issues))
        for issue in unique_issues:
            count = all_issues.count(issue)
            print_error(f"{issue} (occurred {count} time(s))", indent=1)
    
    # Root cause analysis and recommendations
    print(f"\n{Colors.BOLD}Root Cause Analysis & Recommendations:{Colors.RESET}\n")
    
    if public_ip_count > 0:
        print_error("🔍 CRITICAL: Private Link is NOT working (Public IP resolution)")
        print("   Root causes to investigate:")
        print("   1. Private DNS Zone name doesn't match NCC Domain exactly")
        print("   2. Private DNS Zone not linked to VNet with Private Endpoint")
        print("   3. No A record in Private DNS Zone pointing to LB private IP")
        print("   4. NCC Domain configured with protocol/hostname/wildcard (should be zone only)")
        print("   5. Workspace not attached to NCC or NCC not applied")
        print("   6. Private Endpoint not in 'Established' state")
        print("\n   Immediate actions:")
        print("   → Verify: az network private-dns zone show")
        print("   → Verify: az network private-dns record-set a list")
        print("   → Check workspace NCC attachment in Databricks console")
    
    elif dns_failure_count > 0:
        print_error("🔍 DNS Resolution Failures Detected")
        print("   Possible causes:")
        print("   1. Domain doesn't exist in Private DNS Zone")
        print("   2. Typo in domain name")
        print("   3. Private DNS Zone not configured properly")
        print("\n   Immediate actions:")
        print("   → Check DNS records: az network private-dns record-set a list")
        print("   → Verify domain name spelling")
    
    elif tcp_failure_count > 0:
        print_error("🔍 TCP Connection Failures (DNS resolves correctly)")
        print("   Private Link DNS is working, but connectivity fails:")
        print("   1. Load Balancer health probe failing")
        print("   2. Backend pool misconfigured or empty")
        print("   3. NSG blocking traffic from Private Endpoint subnet")
        print("   4. Backend service not listening on the port")
        print("   5. Azure Firewall blocking traffic")
        print("\n   Immediate actions:")
        print("   → Check LB health: az network lb show")
        print("   → Check NSG rules: az network nsg rule list")
        print("   → Verify service is running on backend VM")
    
    elif unreliable_count > 0:
        print_warning("🔍 Intermittent Connection Issues")
        print("   Connections work but are unreliable:")
        print("   1. Backend VM overloaded or unhealthy")
        print("   2. Network congestion")
        print("   3. Load Balancer health probe intermittently failing")
        print("\n   Immediate actions:")
        print("   → Check backend VM performance")
        print("   → Review LB metrics in Azure Monitor")
    
    elif success_count == len(all_results):
        print_success("🎉 All tests PASSED! Private Link is working correctly.")
        print("   Everything is configured properly:")
        print("   ✓ DNS resolves to private IPs")
        print("   ✓ TCP connections succeed")
        print("   ✓ Connections are reliable")

def main():
    """Main execution function"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║     Azure Databricks Private Link Diagnostics - ENHANCED VERSION          ║")
    print("║                    Comprehensive Network Analysis                          ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Diagnostic level: {Colors.GREEN}ENHANCED{Colors.RESET}\n")
    
    # Phase 1: Configuration validation
    print_configuration_validation()
    
    # Phase 2: System diagnostics
    print_system_diagnostics()
    
    # Phase 3: Run comprehensive tests
    print_header("Comprehensive Connectivity Tests")
    
    all_results = []
    for domain_config in DOMAINS_TO_TEST:
        results = run_comprehensive_diagnostics(domain_config)
        all_results.append(results)
    
    # Phase 4: Pattern analysis
    pattern_analysis = analyze_dns_pattern(DOMAINS_TO_TEST)
    
    # Phase 5: Summary and recommendations
    print_comprehensive_summary(all_results, pattern_analysis)
    
    # Phase 6: Export detailed results
    print_header("Detailed Results Export")
    print_info("Copy the JSON below for sharing with support or further analysis:\n")
    
    export_data = {
        'test_metadata': {
            'timestamp': datetime.now().isoformat(),
            'version': '2.0',
            'test_type': 'enhanced'
        },
        'configuration': {
            'private_dns_zone': PRIVATE_DNS_ZONE,
            'ncc_domain': NCC_DOMAIN,
            'expected_ip_prefix': EXPECTED_PRIVATE_IP_PREFIX,
            'expected_lb_ip': EXPECTED_LB_PRIVATE_IP
        },
        'system_info': get_socket_info(),
        'test_results': all_results,
        'pattern_analysis': {k: v for k, v in pattern_analysis.items() if k != 'ip_distribution'}
    }
    
    print(f"{Colors.CYAN}{json.dumps(export_data, indent=2)}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{'='*80}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}{Colors.RESET}\n")

# ============================================================================
# RUN THE ENHANCED DIAGNOSTICS
# ============================================================================

if __name__ == "__main__":
    main()
