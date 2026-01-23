#!/usr/bin/env python3
"""
Quick Result Analyzer for Azure Private Link Diagnostics
=========================================================

This script helps you quickly analyze and compare results from both
Databricks and Azure VM diagnostic tests.

Usage:
    python analyze_results.py

Then paste JSON results from Databricks test when prompted.
Optionally provide Azure VM test results for comparison.
"""

import json
import sys

def print_banner():
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║           Azure Private Link Diagnostics - Result Analyzer                ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()

def analyze_databricks_results(results):
    """Analyze Databricks test results"""
    print("\n📊 DATABRICKS TEST ANALYSIS")
    print("=" * 80)
    
    test_results = results.get('test_results', [])
    if not test_results:
        print("❌ No test results found in JSON")
        return None
    
    analysis = {
        'total': len(test_results),
        'success': 0,
        'dns_failures': 0,
        'public_ip_count': 0,
        'tcp_failures': 0,
        'issues': set()
    }
    
    for result in test_results:
        status = result.get('overall_status')
        
        if status == 'SUCCESS':
            analysis['success'] += 1
            print(f"✅ {result['hostname']}:{result['port']} - PASS")
        elif status == 'PUBLIC_IP_RESOLVED':
            analysis['public_ip_count'] += 1
            print(f"❌ {result['hostname']}:{result['port']} - Public IP (Private Link NOT working)")
        elif status == 'DNS_FAILURE':
            analysis['dns_failures'] += 1
            print(f"❌ {result['hostname']}:{result['port']} - DNS Failed")
        elif status == 'TCP_FAILURE':
            analysis['tcp_failures'] += 1
            print(f"❌ {result['hostname']}:{result['port']} - TCP Connection Failed")
        
        # Collect issues
        issues = result.get('issues_found', [])
        for issue in issues:
            analysis['issues'].add(issue)
    
    print(f"\nSummary: {analysis['success']}/{analysis['total']} tests passed")
    
    return analysis

def get_recommendation(databricks_analysis):
    """Get recommendations based on analysis"""
    print("\n🔍 ROOT CAUSE & RECOMMENDATIONS")
    print("=" * 80)
    
    if databricks_analysis['public_ip_count'] > 0:
        print("\n🚨 CRITICAL ISSUE: Private Link NOT Working")
        print("\nDNS is resolving to PUBLIC IP addresses.")
        print("This means traffic is NOT going through Private Link.\n")
        
        print("ROOT CAUSES TO CHECK:")
        print("  1. Private DNS Zone name ≠ NCC Domain name")
        print("     ➜ Both must match EXACTLY (e.g., 'internal.yourdomain.com')")
        print()
        print("  2. Private DNS Zone not linked to VNet")
        print("     ➜ Check: az network private-dns link vnet list")
        print()
        print("  3. Missing A record in Private DNS Zone")
        print("     ➜ Check: az network private-dns record-set a list")
        print()
        print("  4. NCC Domain misconfigured in Databricks")
        print("     ➜ Should be zone only, no protocol/hostname/wildcards")
        print("     ➜ CORRECT: internal.yourdomain.com")
        print("     ➜ WRONG: https://internal.yourdomain.com")
        print("     ➜ WRONG: *.internal.yourdomain.com")
        print()
        print("  5. Workspace not attached to NCC")
        print("     ➜ Check in Databricks workspace settings")
        print()
        print("  6. Private Endpoint not in 'Established' state")
        print("     ➜ Check in Databricks Account Console → NCC")
        print()
        
        print("IMMEDIATE ACTION ITEMS:")
        print("  [ ] Verify Private DNS Zone name")
        print("  [ ] Verify NCC Domain configuration")
        print("  [ ] Check VNet link: az network private-dns link vnet list")
        print("  [ ] Check DNS records: az network private-dns record-set a list")
        print("  [ ] Verify workspace NCC attachment")
        
    elif databricks_analysis['dns_failures'] > 0:
        print("\n⚠️  DNS RESOLUTION FAILURES")
        print("\nDomains are not resolving at all.\n")
        
        print("ROOT CAUSES TO CHECK:")
        print("  1. DNS record doesn't exist")
        print("     ➜ Add A record: az network private-dns record-set a add-record")
        print()
        print("  2. Typo in domain name")
        print("     ➜ Double-check spelling")
        print()
        print("  3. Private DNS Zone misconfigured")
        print("     ➜ Verify zone exists and is configured correctly")
        
    elif databricks_analysis['tcp_failures'] > 0:
        print("\n⚠️  TCP CONNECTION FAILURES")
        print("\nDNS resolves to private IP (Good!), but connections fail.\n")
        
        print("ROOT CAUSES TO CHECK:")
        print("  1. Load Balancer health probe failing")
        print("     ➜ Check: az network lb probe show")
        print("     ➜ Verify backend targets are healthy")
        print()
        print("  2. NSG blocking Private Endpoint traffic")
        print("     ➜ Check: az network nsg rule list")
        print("     ➜ Allow traffic from Private Endpoint subnet")
        print()
        print("  3. Backend service not running")
        print("     ➜ SSH to backend VM and check: netstat -tlnp")
        print()
        print("  4. Backend pool misconfigured")
        print("     ➜ Check: az network lb address-pool show")
        print()
        print("  5. Azure Firewall blocking traffic")
        print("     ➜ Check firewall rules if present")
        
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("\nPrivate Link is working correctly.")
        print("DNS resolves to private IPs and connections succeed.")

def main():
    print_banner()
    
    print("This tool helps you analyze diagnostic results.\n")
    print("Please paste your Databricks JSON results below.")
    print("(Paste the JSON output from the enhanced diagnostic script)")
    print("When done, press Enter on an empty line, then Ctrl+D (Linux/Mac) or Ctrl+Z (Windows):\n")
    
    # Read JSON from stdin
    json_lines = []
    try:
        while True:
            line = input()
            json_lines.append(line)
    except EOFError:
        pass
    
    json_text = '\n'.join(json_lines)
    
    try:
        results = json.loads(json_text)
        databricks_analysis = analyze_databricks_results(results)
        
        if databricks_analysis:
            get_recommendation(databricks_analysis)
            
            # Show configuration
            print("\n📋 YOUR CONFIGURATION")
            print("=" * 80)
            config = results.get('configuration', {})
            print(f"Private DNS Zone: {config.get('private_dns_zone')}")
            print(f"NCC Domain:       {config.get('ncc_domain')}")
            print(f"Expected IP:      {config.get('expected_ip_prefix')}.x.x")
            
            if config.get('private_dns_zone') == config.get('ncc_domain'):
                print("✅ DNS Zone matches NCC Domain")
            else:
                print("❌ MISMATCH: DNS Zone and NCC Domain are different!")
    
    except json.JSONDecodeError as e:
        print(f"\n❌ Error parsing JSON: {e}")
        print("Please ensure you pasted valid JSON output from the diagnostic script.")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print()

if __name__ == "__main__":
    main()
