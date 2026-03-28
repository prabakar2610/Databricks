#!/bin/bash
# =============================================================
# Databricks Cluster mTLS Network Diagnostic Script
# Run on BOTH clusters and diff the outputs to find differences
# Usage: bash script.sh [target_host] [target_port] [client_cert] [client_key] [ca_cert]
# Example: bash script.sh mtls-endpoint.example.com 443 /etc/ssl/client.crt /etc/ssl/client.key /etc/ssl/ca.crt
# =============================================================

TARGET_HOST="${1:-}"
TARGET_PORT="${2:-443}"
CLIENT_CERT="${3:-}"
CLIENT_KEY="${4:-}"
CA_CERT="${5:-}"

HOSTNAME=$(hostname)
OUTFILE="/tmp/mtls_diag_${HOSTNAME}.txt"
SEPARATOR="================================================================"

# Tee all output to file and stdout
exec > >(tee "$OUTFILE") 2>&1

log_section() { echo ""; echo "$SEPARATOR"; echo ">>> $1"; echo "$SEPARATOR"; }
log_check()   { echo ""; echo "--- $1 ---"; }
ok()          { echo "[OK]  $1"; }
warn()        { echo "[WARN] $1"; }
fail()        { echo "[FAIL] $1"; }
info()        { echo "[INFO] $1"; }

echo "$SEPARATOR"
echo "  CLUSTER mTLS NETWORK DIAGNOSTICS"
echo "  Host      : $HOSTNAME"
echo "  Date (UTC): $(date -u)"
echo "  Target    : ${TARGET_HOST:-'(not specified — skipping connectivity checks)'}"
echo "$SEPARATOR"

# =============================================================
# SECTION 1: SYSTEM INFO
# =============================================================
log_section "SECTION 1: SYSTEM INFO"

log_check "OS Release"
cat /etc/os-release 2>/dev/null || lsb_release -a 2>/dev/null

log_check "Kernel"
uname -a

log_check "Java Version"
java -version 2>&1
info "JAVA_HOME: ${JAVA_HOME:-not set}"

log_check "OpenSSL Version"
openssl version -a

log_check "Python Version"
python3 --version 2>/dev/null

log_check "Databricks Runtime"
echo "DB_HOME: ${DB_HOME:-not set}"
cat /databricks/DBR_VERSION 2>/dev/null || echo "(DBR version file not found)"
env | grep -iE '^DB_|DATABRICKS_RUNTIME' | sort

# =============================================================
# SECTION 2: NETWORK INTERFACE & ROUTING CONFIG
# =============================================================
log_section "SECTION 2: NETWORK INTERFACE & ROUTING CONFIG"

log_check "Network Interfaces (ip addr)"
ip addr show

log_check "Routing Table"
ip route show

log_check "ARP Table"
arp -n 2>/dev/null || ip neigh show

log_check "DNS Config (/etc/resolv.conf)"
cat /etc/resolv.conf

log_check "/etc/hosts"
cat /etc/hosts

log_check "Hostname Resolution"
hostname
hostname -f 2>/dev/null || info "FQDN not available"
hostname -I

# =============================================================
# SECTION 3: PROXY & ENVIRONMENT
# =============================================================
log_section "SECTION 3: PROXY & ENVIRONMENT"

log_check "Proxy Environment Variables"
env | grep -iE 'proxy|no_proxy' | sort
if [[ -z "$(env | grep -iE 'http_proxy|https_proxy')" ]]; then
  info "No HTTP/HTTPS proxy configured"
fi

log_check "SSL/TLS Environment Variables"
env | grep -iE 'ssl|tls|cert|trust|keystore|javax' | sort

log_check "JAVA_OPTS / JVM Flags"
echo "JAVA_OPTS        : ${JAVA_OPTS:-not set}"
echo "SPARK_SUBMIT_OPTS: ${SPARK_SUBMIT_OPTS:-not set}"
echo "_JAVA_OPTIONS    : ${_JAVA_OPTIONS:-not set}"
echo "JDK_JAVA_OPTIONS : ${JDK_JAVA_OPTIONS:-not set}"

# =============================================================
# SECTION 4: SPARK / DATABRICKS TLS CONFIG
# =============================================================
log_section "SECTION 4: SPARK / DATABRICKS TLS CONFIG"

log_check "spark-defaults.conf (SSL/TLS entries)"
SPARK_DEFAULTS="/databricks/spark/conf/spark-defaults.conf"
if [[ -f "$SPARK_DEFAULTS" ]]; then
  grep -iE 'ssl|tls|cert|trust|keystore|key\.' "$SPARK_DEFAULTS" || info "No SSL entries in spark-defaults.conf"
  echo ""
  info "Full spark-defaults.conf:"
  cat "$SPARK_DEFAULTS"
else
  warn "spark-defaults.conf not found at $SPARK_DEFAULTS"
fi

log_check "spark-env.sh (SSL/TLS entries)"
SPARK_ENV="/databricks/spark/conf/spark-env.sh"
if [[ -f "$SPARK_ENV" ]]; then
  grep -iE 'ssl|tls|cert|java|keystore' "$SPARK_ENV" || info "No SSL entries in spark-env.sh"
else
  warn "spark-env.sh not found"
fi

log_check "Databricks deploy.conf (SSL/TLS entries)"
DEPLOY_CONF="/databricks/common/conf/deploy.conf"
if [[ -f "$DEPLOY_CONF" ]]; then
  grep -iE 'ssl|tls|cert|mtls|trust|key' "$DEPLOY_CONF" || info "No SSL entries in deploy.conf"
else
  warn "deploy.conf not found"
fi

log_check "All Databricks conf files with SSL/TLS references"
find /databricks -name "*.conf" -o -name "*.properties" -o -name "*.yaml" -o -name "*.yml" 2>/dev/null \
  | xargs grep -l -iE 'ssl|tls|mtls|cert|keystore|truststore' 2>/dev/null \
  | while read f; do
      echo ""
      echo ">> $f"
      grep -iE 'ssl|tls|mtls|cert|keystore|truststore' "$f"
    done

# =============================================================
# SECTION 5: CERTIFICATES & KEYSTORES
# =============================================================
log_section "SECTION 5: CERTIFICATES & KEYSTORES"

log_check "JVM Default Truststore (cacerts)"
JAVA_BIN=$(readlink -f "$(which java 2>/dev/null)" 2>/dev/null)
if [[ -n "$JAVA_BIN" ]]; then
  JAVA_HOME_GUESS=$(dirname $(dirname "$JAVA_BIN"))
  CACERTS=$(find "$JAVA_HOME_GUESS" -name "cacerts" 2>/dev/null | head -1)
  if [[ -n "$CACERTS" ]]; then
    info "Found cacerts at: $CACERTS"
    info "Truststore entry count: $(keytool -list -keystore "$CACERTS" -storepass changeit 2>/dev/null | grep -c 'trustedCertEntry' || echo 'keytool not available')"
  else
    warn "cacerts not found under $JAVA_HOME_GUESS"
  fi
fi

log_check "Certificate/Keystore Files on Cluster"
find /etc /opt /databricks /tmp /home /root /usr/local \
  \( -name "*.jks" -o -name "*.p12" -o -name "*.pfx" \
     -o -name "*.pem" -o -name "*.crt" -o -name "*.cer" \
     -o -name "*.key" -o -name "truststore" -o -name "keystore" \) \
  2>/dev/null | grep -v "^Binary" | sort

log_check "System CA Certificates"
echo "Certs in /etc/ssl/certs/:"
ls /etc/ssl/certs/ 2>/dev/null | wc -l
ls /usr/local/share/ca-certificates/ 2>/dev/null

log_check "Init Scripts (cert injection may be here)"
echo "Init script dirs:"
ls /databricks/init_scripts/ 2>/dev/null || info "/databricks/init_scripts/ not found"
ls /databricks/driver/logs/init_scripts/ 2>/dev/null | head -20 || info "Init script logs not found"

log_check "Client Cert Details (if provided)"
if [[ -f "$CLIENT_CERT" ]]; then
  openssl x509 -in "$CLIENT_CERT" -text -noout 2>/dev/null | grep -E 'Subject:|Issuer:|Not Before|Not After|Extended Key'
  # Check expiry
  EXPIRY=$(openssl x509 -in "$CLIENT_CERT" -noout -enddate 2>/dev/null | cut -d= -f2)
  EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null)
  NOW_EPOCH=$(date +%s)
  DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
  if [[ $DAYS_LEFT -lt 0 ]]; then
    fail "Client cert EXPIRED $((DAYS_LEFT * -1)) days ago"
  elif [[ $DAYS_LEFT -lt 30 ]]; then
    warn "Client cert expires in $DAYS_LEFT days"
  else
    ok "Client cert valid for $DAYS_LEFT more days"
  fi
else
  info "No client cert path provided (pass as arg 3)"
fi

log_check "CA Cert Details (if provided)"
if [[ -f "$CA_CERT" ]]; then
  openssl x509 -in "$CA_CERT" -text -noout 2>/dev/null | grep -E 'Subject:|Issuer:|Not Before|Not After|CA:TRUE'
else
  info "No CA cert path provided (pass as arg 5)"
fi

# =============================================================
# SECTION 6: FIREWALL & PORT RULES
# =============================================================
log_section "SECTION 6: FIREWALL & PORT RULES"

log_check "iptables Rules"
iptables -L -n -v 2>/dev/null || warn "iptables not available or no permission"

log_check "iptables NAT"
iptables -t nat -L -n 2>/dev/null || true

log_check "Active Connections"
ss -tnp 2>/dev/null || netstat -tnp 2>/dev/null

log_check "Listening Ports"
ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null

# =============================================================
# SECTION 7: ACTIVE NETWORK CHECKS
# (skipped if no TARGET_HOST provided)
# =============================================================
log_section "SECTION 7: ACTIVE NETWORK CHECKS (target: ${TARGET_HOST:-SKIPPED})"

if [[ -z "$TARGET_HOST" ]]; then
  warn "No target host specified. Pass as first argument to enable connectivity checks."
else

  log_check "DNS Resolution"
  if nslookup "$TARGET_HOST" 2>/dev/null; then
    ok "DNS resolved $TARGET_HOST"
  else
    fail "DNS resolution failed for $TARGET_HOST"
  fi
  dig "$TARGET_HOST" 2>/dev/null || host "$TARGET_HOST" 2>/dev/null

  log_check "TCP Connectivity (port $TARGET_PORT)"
  if timeout 10 bash -c "echo >/dev/tcp/$TARGET_HOST/$TARGET_PORT" 2>/dev/null; then
    ok "TCP connection to $TARGET_HOST:$TARGET_PORT succeeded"
  else
    fail "TCP connection to $TARGET_HOST:$TARGET_PORT FAILED"
  fi

  log_check "ICMP Ping"
  if ping -c 4 -W 3 "$TARGET_HOST" 2>/dev/null; then
    ok "Ping to $TARGET_HOST succeeded"
  else
    warn "Ping failed (may be blocked by firewall — not necessarily an error)"
  fi

  log_check "Traceroute"
  traceroute -m 15 -w 2 "$TARGET_HOST" 2>/dev/null || \
    tracepath -m 15 "$TARGET_HOST" 2>/dev/null || \
    warn "traceroute/tracepath not available"

  # ---------------------------------------------------------
  log_check "TLS Handshake — Server Certificate Chain"
  openssl s_client \
    -connect "${TARGET_HOST}:${TARGET_PORT}" \
    -servername "$TARGET_HOST" \
    -showcerts \
    </dev/null 2>&1 | head -80
  HANDSHAKE_STATUS=${PIPESTATUS[0]}
  [[ $HANDSHAKE_STATUS -eq 0 ]] && ok "TLS handshake succeeded" || fail "TLS handshake failed (exit $HANDSHAKE_STATUS)"

  # ---------------------------------------------------------
  log_check "mTLS Handshake (with client cert)"
  if [[ -f "$CLIENT_CERT" && -f "$CLIENT_KEY" ]]; then
    MTLS_CMD="openssl s_client -connect ${TARGET_HOST}:${TARGET_PORT} -servername $TARGET_HOST -cert $CLIENT_CERT -key $CLIENT_KEY"
    [[ -f "$CA_CERT" ]] && MTLS_CMD="$MTLS_CMD -CAfile $CA_CERT"
    MTLS_CMD="$MTLS_CMD -showcerts"
    eval "$MTLS_CMD </dev/null 2>&1" | head -80
    MTLS_STATUS=${PIPESTATUS[0]}
    [[ $MTLS_STATUS -eq 0 ]] && ok "mTLS handshake succeeded" || fail "mTLS handshake failed (exit $MTLS_STATUS)"
  else
    warn "Skipping mTLS test — client cert/key not provided (args 3 and 4)"
  fi

  # ---------------------------------------------------------
  log_check "TLS Protocol Version Support"
  for PROTO in tls1 tls1_1 tls1_2 tls1_3; do
    RESULT=$(openssl s_client -connect "${TARGET_HOST}:${TARGET_PORT}" \
      -servername "$TARGET_HOST" \
      -${PROTO} </dev/null 2>&1)
    if echo "$RESULT" | grep -q "Cipher is"; then
      CIPHER=$(echo "$RESULT" | grep "Cipher is" | head -1)
      ok "Protocol -${PROTO}: ACCEPTED | $CIPHER"
    else
      ERR=$(echo "$RESULT" | grep -iE 'error|alert|wrong|no proto' | head -1)
      fail "Protocol -${PROTO}: REJECTED | ${ERR}"
    fi
  done

  # ---------------------------------------------------------
  log_check "Negotiated Cipher Suite"
  openssl s_client \
    -connect "${TARGET_HOST}:${TARGET_PORT}" \
    -servername "$TARGET_HOST" \
    </dev/null 2>&1 | grep -E 'Cipher|Protocol|Session-ID|Verify' | head -20

  # ---------------------------------------------------------
  log_check "Server Certificate Details"
  openssl s_client \
    -connect "${TARGET_HOST}:${TARGET_PORT}" \
    -servername "$TARGET_HOST" \
    </dev/null 2>&1 \
  | openssl x509 -noout -text 2>/dev/null \
  | grep -E 'Subject:|Issuer:|Not Before|Not After|Alt|Extended|DNS:|IP:' \
  || warn "Could not extract server cert details"

  # ---------------------------------------------------------
  log_check "Server Certificate Expiry"
  EXPIRY=$(openssl s_client -connect "${TARGET_HOST}:${TARGET_PORT}" \
    -servername "$TARGET_HOST" </dev/null 2>&1 \
    | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  if [[ -n "$EXPIRY" ]]; then
    EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null)
    NOW_EPOCH=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
    if [[ $DAYS_LEFT -lt 0 ]]; then
      fail "Server cert EXPIRED $((DAYS_LEFT * -1)) days ago"
    elif [[ $DAYS_LEFT -lt 30 ]]; then
      warn "Server cert expires in $DAYS_LEFT days"
    else
      ok "Server cert valid for $DAYS_LEFT more days"
    fi
  fi

  # ---------------------------------------------------------
  log_check "Certificate Verification Against System CAs"
  openssl s_client \
    -connect "${TARGET_HOST}:${TARGET_PORT}" \
    -servername "$TARGET_HOST" \
    -verify_return_error \
    </dev/null 2>&1 | grep -E 'Verify|verify|error|OK' | head -10

  if [[ -f "$CA_CERT" ]]; then
    log_check "Certificate Verification Against Provided CA"
    openssl s_client \
      -connect "${TARGET_HOST}:${TARGET_PORT}" \
      -servername "$TARGET_HOST" \
      -CAfile "$CA_CERT" \
      -verify_return_error \
      </dev/null 2>&1 | grep -E 'Verify|verify|error|OK' | head -10
  fi

  # ---------------------------------------------------------
  log_check "HTTP(S) Connectivity Test (curl)"
  curl -v --max-time 15 \
    ${CLIENT_CERT:+--cert "$CLIENT_CERT"} \
    ${CLIENT_KEY:+--key "$CLIENT_KEY"} \
    ${CA_CERT:+--cacert "$CA_CERT"} \
    "https://${TARGET_HOST}:${TARGET_PORT}/" 2>&1 | head -60
  CURL_STATUS=$?
  [[ $CURL_STATUS -eq 0 || $CURL_STATUS -eq 22 ]] \
    && ok "curl connected (HTTP status may be non-200 but TLS worked)" \
    || fail "curl failed with exit code $CURL_STATUS"

fi  # end TARGET_HOST check

# =============================================================
# SECTION 8: OPENSSL AVAILABLE CIPHERS
# =============================================================
log_section "SECTION 8: AVAILABLE CIPHER SUITES"

log_check "OpenSSL Supported Ciphers"
openssl ciphers -v 'ALL:COMPLEMENTOFALL' 2>/dev/null | awk '{printf "%-40s %s %s\n", $1, $2, $4}' | sort

# =============================================================
# SECTION 9: JAVA TLS DEBUG (if keytool available)
# =============================================================
log_section "SECTION 9: JAVA KEYSTORE / TRUSTSTORE DETAILS"

log_check "javax.net.ssl JVM Properties (from running JVM if accessible)"
JINFO=$(which jinfo 2>/dev/null)
if [[ -n "$JINFO" ]]; then
  SPARK_PID=$(pgrep -f 'SparkSubmit|CoarseGrainedExecutorBackend|DatabricksDriver' | head -1)
  if [[ -n "$SPARK_PID" ]]; then
    info "Spark PID: $SPARK_PID"
    jinfo "$SPARK_PID" 2>/dev/null | grep -iE 'ssl|tls|trust|keystore|cert|javax' || info "No SSL JVM flags found"
  fi
else
  info "jinfo not available"
fi

log_check "Custom Truststore Entries (if JKS found)"
find /etc /opt /databricks /tmp -name "*.jks" 2>/dev/null | head -3 | while read jks; do
  echo ">> $jks"
  keytool -list -keystore "$jks" -storepass changeit 2>/dev/null \
    || keytool -list -keystore "$jks" -storepass "" 2>/dev/null \
    || warn "Could not list $jks (wrong password or not readable)"
done

# =============================================================
# DONE
# =============================================================
log_section "DIAGNOSTICS COMPLETE"
echo "Output saved to: $OUTFILE"
echo ""
echo "To copy to DBFS (run in notebook cell):"
echo "  dbutils.fs.cp('file://$OUTFILE', 'dbfs:/tmp/mtls_diag_${HOSTNAME}.txt')"
echo ""
echo "To diff two cluster outputs:"
echo "  diff mtls_diag_good_cluster.txt mtls_diag_bad_cluster.txt"
