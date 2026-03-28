# Cluster mTLS Network Diagnostics

**Config collection and active TLS/mTLS checks from Databricks cluster workers**

## Overview

This Bash script gathers system, network, Spark/Databricks TLS configuration, certificate inventory, and (optionally) runs live connectivity and handshake tests against a target host. Use it when **mutual TLS (mTLS)** or TLS to an internal endpoint works on one cluster but not another: run the same script on both clusters, save outputs, and **diff** them.

**Run time:** ~2–5 minutes (depends on target checks and cluster I/O)  
**Environment:** Databricks notebook **`%sh`** on cluster-attached compute (driver or worker context matches where you run the cell)

---

## When to use

- mTLS or HTTPS to an API fails from one cluster policy or pool but not another  
- Suspected differences in Java/OpenSSL, proxy env, Spark SSL settings, or truststores  
- Need a single artifact for support: routing, DNS, firewall, cert paths, and handshake results  

---

## Usage

### Arguments

```text
bash script.sh [target_host] [target_port] [client_cert] [client_key] [ca_cert]
```

| Arg | Position | Required | Description |
|-----|----------|----------|-------------|
| Target host | 1 | No* | Hostname for DNS/TCP/TLS/mTLS checks. Omit to skip Section 7 only. |
| Target port | 2 | No | Default `443`. |
| Client certificate | 3 | No | PEM client cert for mTLS and curl. |
| Client private key | 4 | No | PEM key for client cert. |
| CA certificate | 5 | No | PEM CA for `-CAfile` / curl `--cacert`. |

\* Sections 1–6, 8–9 always run. Section 7 runs only if `target_host` is non-empty.

### Method 1: Download from GitHub (recommended)

In a notebook cell:

```python
import urllib.request
url = "https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/mtls_cluster_diagnostics/script.sh"
urllib.request.urlretrieve(url, "/tmp/mtls_cluster_diag.sh")
```

Then in **`%sh`**:

```bash
chmod +x /tmp/mtls_cluster_diag.sh
bash /tmp/mtls_cluster_diag.sh mtls-endpoint.example.com 443 /etc/ssl/client.crt /etc/ssl/client.key /etc/ssl/ca.crt
```

### Method 2: Inline write + run

**Cell 1 — write script**

```python
script = open("/path/to/script.sh").read()  # or paste the file contents as a triple-quoted string
with open("/tmp/mtls_diag.sh", "w") as f:
    f.write(script)
```

**Cell 2 — run**

```bash
%sh
bash /tmp/mtls_diag.sh mtls-endpoint.example.com 443 /etc/ssl/client.crt /etc/ssl/client.key /etc/ssl/ca.crt
```

### Save output to DBFS (compare clusters)

Output is tee’d to stdout and to `/tmp/mtls_diag_<hostname>.txt` on that node.

```python
import subprocess
hostname = subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip()
dbutils.fs.cp(f"file:///tmp/mtls_diag_{hostname}.txt", f"dbfs:/tmp/mtls_diag_{hostname}.txt")
print(f"Saved: dbfs:/tmp/mtls_diag_{hostname}.txt")
```

Download both files locally, then:

```bash
diff mtls_diag_good_cluster.txt mtls_diag_bad_cluster.txt
```

---

## What each section catches (mTLS / TLS)

| Section | What it finds |
|---------|----------------|
| 1 — System info | Java/OpenSSL/runtime mismatch between clusters |
| 2 — Network / routing | Different subnet, gateway, interfaces, DNS resolver |
| 3 — Proxy / env | Proxy or SSL-related env only on one side |
| 4 — Spark / Databricks TLS | `spark.ssl.*`, deploy.conf, or other TLS-related conf differences |
| 5 — Certs / keystores | Missing or expired client cert, different trust material, init scripts |
| 6 — Firewall | Local `iptables` / listening ports / connection state |
| 7 — Active checks | TCP reachability, TLS and mTLS handshakes, protocol/cipher negotiation, cert expiry, curl HTTPS |
| 8 — Cipher suites | OpenSSL-supported ciphers (cipher mismatch hints) |
| 9 — Java keystore | JVM / JKS listing when readable; optional `jinfo` on Spark-related PID |

---

## Security and operations notes

- **Secrets:** Client keys and cert paths appear in process listings only while commands run; avoid logging paths that expose sensitive mount points in shared notebooks.  
- **Permissions:** Some checks (`iptables`, `jinfo`, reading certain keystores) may need capabilities the cluster user has on DBR; failures are reported as warnings, not necessarily cluster misconfiguration.  
- **Target scope:** Use only hosts you are authorized to test. Aggressive scanning is unnecessary; this script uses short timeouts and standard tools.  

---

## Related scripts

- [Private Link Diagnostics](../private_link_diagnostics/README.md) — private connectivity and DNS to internal hosts  
- [DNS Diagnostics](../dns_diagnostics/README.md) — resolution and resolver configuration  

---

## Links

- **Repository:** [https://github.com/prabakar2610/Databricks](https://github.com/prabakar2610/Databricks)  
- **Raw script:** [script.sh](https://raw.githubusercontent.com/prabakar2610/Databricks/master/network_analysis/databricks_notebooks/mtls_cluster_diagnostics/script.sh)  
- **Network analysis home:** [../../README.md](../../README.md)  

---

**Version:** 1.0  
**Last updated:** 2026-03-28  
