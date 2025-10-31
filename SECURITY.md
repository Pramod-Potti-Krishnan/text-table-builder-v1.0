# Project Security Guide

This project uses a high-security authentication model for Google Cloud Platform services.

---

## 1. Authentication

We use the **Application Default Credentials (ADC)** pattern for Google Cloud authentication. This allows the same code to work seamlessly in both local development and production environments without any code changes.

### Local Development

Authentication is handled by the `gcloud` CLI. Developers must run the following command before running the application:

```bash
gcloud auth application-default login
```

This command:
- Opens a browser window for Google authentication
- Stores your personal credentials locally in `~/.config/gcloud/application_default_credentials.json`
- Allows the application to authenticate as YOU when running locally

**Required Environment Variables for Local**:
```bash
GCP_PROJECT_ID=deckster-xyz       # Your GCP project ID
GCP_LOCATION=us-central1          # GCP region (optional, defaults to us-central1)
# DO NOT set GCP_SERVICE_ACCOUNT_JSON locally
```

**Local Setup Steps**:
1. Install Google Cloud SDK: `brew install google-cloud-sdk` (macOS) or download from https://cloud.google.com/sdk/docs/install
2. Authenticate: `gcloud auth application-default login`
3. Set project: `gcloud config set project deckster-xyz`
4. Copy `.env.example` to `.env` and configure `GCP_PROJECT_ID`
5. Run the application: `python main.py`

### Production (Railway)

Authentication is handled by a **Service Account** (a "robot" account with specific permissions). The `GCP_SERVICE_ACCOUNT_JSON` environment variable must be set to the full JSON content of the service account key.

**Required Environment Variables for Railway**:
```bash
GCP_PROJECT_ID=deckster-xyz                   # Your GCP project ID
GCP_LOCATION=us-central1                      # GCP region
GCP_SERVICE_ACCOUNT_JSON={"type":"service_account",...}  # Full service account JSON
```

**Railway Setup Steps**:
1. Go to Railway dashboard: https://railway.app/dashboard
2. Select your deployment: **web-production-e3796**
3. Navigate to: **Variables** tab
4. Add the three environment variables listed above
5. Deploy the code (Railway will use the service account credentials)

**How to Get Service Account JSON**:
1. Go to: https://console.cloud.google.com
2. Navigate to: **IAM & Admin** → **Service Accounts**
3. Find or create a service account
4. Click **Actions** (⋮) → **Manage Keys**
5. Click **Add Key** → **Create New Key** → **JSON**
6. Download the JSON file
7. Copy the **entire JSON content** (one long line) into Railway's `GCP_SERVICE_ACCOUNT_JSON` variable

---

## 2. Security Best Practices

### GCP Quotas

All APIs used in this project (like `aiplatform.googleapis.com` for Vertex AI) should have **low daily usage quotas** set in the GCP Console to prevent runaway costs from a security breach.

**Recommended Quotas**:
- **Vertex AI API**: Set daily request limits appropriate for your usage
- **Gemini Models**: Enable quota alerts at 80% usage
- **Monitor billing**: Set up billing alerts and budget limits

**To Set Quotas**:
1. Go to: https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/quotas
2. Select your project
3. Filter for relevant quotas
4. Click **Edit Quotas** and set appropriate limits
5. Enable notifications for quota usage

### Railway Security

The Railway project must have **Multi-Factor Authentication (MFA)** enabled for all collaborators.

**Enable MFA**:
1. Go to Railway account settings
2. Navigate to **Security**
3. Enable **Two-Factor Authentication (2FA)**
4. Require 2FA for all team members

**Additional Railway Security**:
- Use Railway's **Private Networking** for internal services
- Rotate service account credentials regularly (every 90 days)
- Use Railway's **Secrets** feature for sensitive environment variables
- Enable Railway's **Audit Log** to track configuration changes

### IP Allowlist (v3.3 Security Feature)

The application implements **IP-based access control** to restrict API access to authorized IP addresses only. This prevents unauthorized usage even if someone discovers your Railway URL.

**Features**:
- Restricts all API endpoints to whitelisted IPs
- Health check endpoint (`/health`) remains publicly accessible for Railway monitoring
- Supports both IPv4 and IPv6 addresses
- Handles proxy headers (X-Forwarded-For, X-Real-IP) correctly on Railway
- Logs all access attempts for security auditing

**Configuration**:
```bash
# Format: Comma-separated list of IP addresses
ALLOWED_IPS=127.0.0.1,::1,174.206.231.36,<director-agent-railway-ip>
```

**Local Development IPs to Include**:
- `127.0.0.1` - IPv4 localhost
- `::1` - IPv6 localhost
- Your development machine's public IP (find with: `curl ifconfig.me`)

**Railway Production IPs to Include**:
- Your development machine IP (for testing)
- Director Agent's Railway outbound IP
- Any other authorized services that need to call this API

**How to Find Railway Service Outbound IP**:
1. Check Railway deployment logs for IP addresses
2. Or temporarily disable IP allowlist and check logs for incoming IPs
3. Or contact Railway support for static IP information

**Security Benefits**:
- Prevents quota exhaustion from unauthorized users
- Reduces attack surface for DDoS attempts
- Provides audit trail of access attempts
- No impact on Railway's health check monitoring

**Testing IP Allowlist**:
```bash
# Should succeed (your IP is allowed)
curl https://web-production-e3796.up.railway.app/health

# API endpoints require allowed IP
curl -X POST https://web-production-e3796.up.railway.app/api/v1/generate/text \
  -H "Content-Type: application/json" \
  -d '{"slide_id": "test", ...}'
```

**Important Notes**:
- Leave `ALLOWED_IPS` empty to disable restrictions (NOT RECOMMENDED for production)
- Update the allowlist whenever your IP changes or new services are authorized
- Railway environment variable changes take effect immediately (no redeployment needed)

### Private Networking

Any database connections should use Railway's **private networking** feature, not the public internet. This ensures database traffic never leaves Railway's internal network.

**Setup Private Networking**:
1. In Railway dashboard, navigate to your service
2. Go to **Networking** tab
3. Enable **Private Network**
4. Use internal hostnames (e.g., `service-name.railway.internal`) for service-to-service communication

---

## 3. Service Account Permissions

The service account used in production should follow the **principle of least privilege**. Grant only the minimum permissions required for the application to function.

**Required Permissions**:
- **Vertex AI User** (`roles/aiplatform.user`) - For accessing Gemini models via Vertex AI

**How to Set Permissions**:
1. Go to: https://console.cloud.google.com/iam-admin/iam
2. Find your service account
3. Click **Edit** (pencil icon)
4. Add role: **Vertex AI User**
5. Save changes

**Optional Permissions** (if needed):
- **Logs Writer** (`roles/logging.logWriter`) - If sending logs to Cloud Logging
- **Monitoring Metric Writer** (`roles/monitoring.metricWriter`) - If sending metrics to Cloud Monitoring

---

## 4. Credential Rotation

Service account credentials should be rotated regularly to minimize security risks.

**Rotation Schedule**:
- **Every 90 days**: Rotate service account keys
- **After any security incident**: Immediately rotate all credentials
- **When team members leave**: Rotate and review all shared credentials

**How to Rotate**:
1. Create a new service account key (as described in "How to Get Service Account JSON")
2. Update Railway environment variable `GCP_SERVICE_ACCOUNT_JSON` with new key
3. Test that the new key works
4. Delete the old key from GCP Console

---

## 5. Monitoring & Auditing

### GCP Audit Logs

Enable Cloud Audit Logs to track all API usage and authentication attempts.

**Enable Audit Logs**:
1. Go to: https://console.cloud.google.com/iam-admin/audit
2. Find **Vertex AI API**
3. Enable **Admin Read**, **Data Read**, and **Data Write** logs
4. Set up log export to BigQuery for long-term storage and analysis

### Railway Deployment Logs

Monitor Railway deployment logs for:
- Successful Vertex AI initialization: `"Initialized Vertex AI with service account"`
- Authentication errors: `"Failed to initialize Vertex AI"`
- Unexpected API key references (should be NONE)

**View Logs**:
1. Railway dashboard → Select deployment
2. Click **Deployments** → Select latest deployment
3. Click **View Logs**
4. Filter for security-related messages

---

## 6. Incident Response

If you suspect a security breach:

1. **Immediate Actions**:
   - Disable the compromised service account in GCP Console
   - Rotate all credentials immediately
   - Review audit logs for unauthorized access
   - Check billing for unexpected charges

2. **Investigation**:
   - Review GCP Audit Logs for suspicious activity
   - Check Railway deployment logs for anomalies
   - Verify all environment variables are correct
   - Scan codebase for any hardcoded credentials

3. **Recovery**:
   - Create new service account with minimal permissions
   - Update Railway environment variables with new credentials
   - Redeploy the application
   - Monitor closely for 48 hours

4. **Post-Incident**:
   - Document the incident and response
   - Update security procedures if needed
   - Review and tighten GCP quotas
   - Consider additional monitoring/alerting

---

## 7. Development Guidelines

### For Developers

- **NEVER** hardcode API keys, credentials, or secrets in code
- **ALWAYS** use environment variables for configuration
- **NEVER** commit `.env` files to version control (already in `.gitignore`)
- **ALWAYS** use `.env.example` as a template
- **NEVER** share service account JSON files via Slack, email, or other channels
- **ALWAYS** use Railway's secure variable storage for production credentials

### Code Review Checklist

Before merging code:
- [ ] No hardcoded credentials in code
- [ ] No API keys in configuration files
- [ ] All secrets use environment variables
- [ ] `.env` is in `.gitignore`
- [ ] Documentation updated if authentication changes
- [ ] Tests pass locally with ADC
- [ ] Deployment tested on Railway with service account

---

## 8. Security Contacts

**For Security Issues**:
- Report immediately to: [Your security team email]
- GCP Security: https://cloud.google.com/security/disclosure
- Railway Support: https://railway.app/help

**Resources**:
- GCP Security Best Practices: https://cloud.google.com/security/best-practices
- Railway Security: https://docs.railway.app/reference/security
- Vertex AI Security: https://cloud.google.com/vertex-ai/docs/general/security

---

**Last Updated**: October 31, 2025
**Version**: 1.0 (ADC Authentication Pattern)
**Author**: Security Team
