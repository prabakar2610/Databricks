# Databricks Private Link Diagnostics - Notebook Examples

This file shows different ways to run the diagnostic script in Databricks notebooks.

## 📌 Prerequisites

1. Upload the scripts to GitHub (public or private repository)
2. Get the "Raw" URL for the script files
3. Update the URLs in the examples below

---

## 🚀 Method 1: Simple One-Liner (Easiest)

**Step 1:** Upload `run_diagnostics.py` to your GitHub repo and update the configuration inside it

**Step 2:** In your Databricks notebook, run this single cell:

```python
import requests; exec(requests.get("https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/run_diagnostics.py").text)
```

✅ **Pros:** 
- One line of code
- Configuration stored in GitHub
- Easy to share with team

❌ **Cons:** 
- Need to update GitHub to change configuration

---

## 🔧 Method 2: Configure in Notebook (More Flexible)

**In Cell 1 - Configuration:**

```python
# Your configuration
DOMAINS_TO_TEST = [
    {"host": "api.internal.yourdomain.com", "port": 443, "description": "API Service"},
]
PRIVATE_DNS_ZONE = "internal.yourdomain.com"
NCC_DOMAIN = "internal.yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"
EXPECTED_LB_PRIVATE_IP = "10.0.1.100"

# Test settings (optional)
DNS_RETRY_COUNT = 5
TCP_RETRY_COUNT = 3
ENABLE_PORT_SCANNING = True
```

**In Cell 2 - Download and Run:**

```python
import requests

SCRIPT_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/databricks_private_link_diagnostics_enhanced.py"

# Download and execute
response = requests.get(SCRIPT_URL)
if response.status_code == 200:
    exec(response.text)
else:
    print(f"❌ Failed to download: HTTP {response.status_code}")
```

✅ **Pros:** 
- Configuration in notebook (easy to change)
- No need to update GitHub for config changes
- Full control

❌ **Cons:** 
- Two cells instead of one

---

## 📦 Method 3: Clone and Run (For Multiple Files)

```python
# Clone the entire repository
%sh
rm -rf /tmp/pl-diagnostics
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git /tmp/pl-diagnostics

# Update configuration
DOMAINS_TO_TEST = [{"host": "api.internal.yourdomain.com", "port": 443}]
PRIVATE_DNS_ZONE = "internal.yourdomain.com"
NCC_DOMAIN = "internal.yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

# Run the main script
%run /tmp/pl-diagnostics/databricks_private_link_diagnostics_enhanced.py
```

✅ **Pros:** 
- Works with private repositories (with credentials)
- Can access multiple files
- Local copy for offline use

❌ **Cons:** 
- More complex
- Requires git

---

## 🔐 Method 4: Private Repository with Authentication

```python
import requests
import base64

# GitHub Personal Access Token (create at: https://github.com/settings/tokens)
GITHUB_TOKEN = dbutils.secrets.get(scope="your-scope", key="github-token")

# Raw URL
SCRIPT_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/PRIVATE-REPO/main/databricks_private_link_diagnostics_enhanced.py"

# Configuration
DOMAINS_TO_TEST = [{"host": "api.internal.yourdomain.com", "port": 443}]
PRIVATE_DNS_ZONE = "internal.yourdomain.com"
NCC_DOMAIN = "internal.yourdomain.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"

# Download with authentication
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
response = requests.get(SCRIPT_URL, headers=headers)

if response.status_code == 200:
    exec(response.text)
else:
    print(f"❌ Failed: HTTP {response.status_code}")
```

✅ **Pros:** 
- Works with private repositories
- Secure (token in Databricks secrets)

❌ **Cons:** 
- Requires setup of GitHub token and Databricks secrets

---

## 🎯 Recommended Setup

### For Quick Testing:
Use **Method 2** - Configure in notebook, download and run

### For Production/Team Use:
Use **Method 1** - One-liner with `run_diagnostics.py`

### For Private/Sensitive Configs:
Use **Method 4** - Private repo with authentication

---

## 📝 Complete Example (Copy-Paste Ready)

```python
# ============================================================================
# Databricks Private Link Diagnostics - Quick Start
# ============================================================================

# STEP 1: Configure your environment
DOMAINS_TO_TEST = [
    {"host": "YOUR-SERVICE.YOUR-DOMAIN.com", "port": 443, "description": "My Service"},
]
PRIVATE_DNS_ZONE = "YOUR-DOMAIN.com"
NCC_DOMAIN = "YOUR-DOMAIN.com"
EXPECTED_PRIVATE_IP_PREFIX = "10.0"  # First 2 octets of your VNet
EXPECTED_LB_PRIVATE_IP = None  # Set to specific IP if known, or None

# STEP 2: Download and run diagnostic script
import requests

SCRIPT_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/databricks_private_link_diagnostics_enhanced.py"

print("📥 Downloading diagnostic script...")
response = requests.get(SCRIPT_URL)

if response.status_code == 200:
    print("✅ Downloaded successfully")
    print("🚀 Running diagnostics...\n")
    exec(response.text)
else:
    print(f"❌ Failed to download: HTTP {response.status_code}")
    print(f"URL: {SCRIPT_URL}")
```

---

## 🔗 Getting the Raw GitHub URL

1. Go to your file on GitHub
2. Click the "Raw" button (top right of file view)
3. Copy the URL from your browser
4. It should look like: `https://raw.githubusercontent.com/username/repo/branch/filename.py`

---

## 💡 Tips

1. **Use Raw URLs:** Always use `raw.githubusercontent.com`, not `github.com`
2. **Branch Names:** Use `main` or `master` depending on your default branch
3. **Caching:** GitHub caches raw files for ~5 minutes. If you update the script, wait a bit or add `?nocache=1` to URL
4. **Testing:** Test with the basic script first, then move to enhanced

---

## 🐛 Troubleshooting

**Error: "HTTP 404"**
- Check the URL is correct
- Ensure you're using the raw URL
- Verify the branch name (main vs master)

**Error: "HTTP 403"**
- Private repo requires authentication (use Method 4)

**Error: "Module not found"**
- The script uses only Python standard library, so this shouldn't happen
- If it does, check your Databricks runtime version

**Script runs but no output:**
- Check your configuration variables are set before running exec()
- Ensure variable names match exactly (case-sensitive)

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your GitHub URL works in a browser
3. Test with a simple print statement first: `exec("print('Test successful!')")`
