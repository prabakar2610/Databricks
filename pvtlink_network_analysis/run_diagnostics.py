"""
Databricks Private Link Diagnostics - Easy Runner
==================================================

Simple wrapper to run diagnostics from GitHub with minimal configuration.

Usage in Databricks Notebook:
------------------------------

import requests
exec(requests.get("YOUR_GITHUB_RAW_URL/run_diagnostics.py").text)

"""

# ============================================================================
# QUICK CONFIGURATION - Update these values
# ============================================================================

CONFIG = {
    # List of services to test
    "domains": [
        {"host": "api.internal.yourdomain.com", "port": 443, "description": "API Service HTTPS"},
        {"host": "api.internal.yourdomain.com", "port": 80, "description": "API Service HTTP"},
    ],
    
    # DNS and NCC configuration
    "private_dns_zone": "internal.yourdomain.com",
    "ncc_domain": "internal.yourdomain.com",
    
    # Expected network configuration
    "expected_ip_prefix": "10.0",
    "expected_lb_ip": "10.0.1.100",  # Optional, set to None if unknown
    
    # Test configuration
    "dns_retry_count": 5,
    "tcp_retry_count": 3,
    "connection_timeout": 5,
    
    # Feature flags
    "enable_port_scanning": True,
    "enable_multiple_resolution_tests": True,
    "enable_latency_analysis": True,
    "enable_external_connectivity_test": True,
}

# ============================================================================
# Auto-download and run the main diagnostic script
# ============================================================================

def run_diagnostics(config=None):
    """Run diagnostics with the provided configuration"""
    import requests
    
    if config is None:
        config = CONFIG
    
    # GitHub raw URL for the main diagnostic script
    # UPDATE THIS with your actual GitHub repo URL
    SCRIPT_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/databricks_private_link_diagnostics_enhanced.py"
    
    print("📥 Downloading diagnostic script from GitHub...")
    response = requests.get(SCRIPT_URL)
    
    if response.status_code != 200:
        print(f"❌ Failed to download script: HTTP {response.status_code}")
        return
    
    print("✅ Script downloaded successfully")
    print("🚀 Running diagnostics...\n")
    
    # Set configuration in global namespace
    globals().update({
        'DOMAINS_TO_TEST': config['domains'],
        'PRIVATE_DNS_ZONE': config['private_dns_zone'],
        'NCC_DOMAIN': config['ncc_domain'],
        'EXPECTED_PRIVATE_IP_PREFIX': config['expected_ip_prefix'],
        'EXPECTED_LB_PRIVATE_IP': config.get('expected_lb_ip'),
        'DNS_RETRY_COUNT': config.get('dns_retry_count', 5),
        'TCP_RETRY_COUNT': config.get('tcp_retry_count', 3),
        'CONNECTION_TIMEOUT': config.get('connection_timeout', 5),
        'ENABLE_PORT_SCANNING': config.get('enable_port_scanning', True),
        'ENABLE_MULTIPLE_RESOLUTION_TESTS': config.get('enable_multiple_resolution_tests', True),
        'ENABLE_LATENCY_ANALYSIS': config.get('enable_latency_analysis', True),
        'ENABLE_EXTERNAL_CONNECTIVITY_TEST': config.get('enable_external_connectivity_test', True),
    })
    
    # Execute the main script
    exec(response.text, globals())

# Run automatically if this script is executed directly
if __name__ == "__main__":
    run_diagnostics()
