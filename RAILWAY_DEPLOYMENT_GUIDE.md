# 🚨 URGENT: Text Service Security Fix - Railway Deployment Guide

**Status**: Code updated, waiting for Railway deployment
**Date**: October 31, 2025
**Priority**: CRITICAL SECURITY FIX

---

## What Changed

✅ **Code Updated** (completed):
- `app/core/llm_client.py` - Migrated from API key to Vertex AI service account auth
- `requirements.txt` - Added `google-cloud-aiplatform>=1.70.0`

⚠️ **Railway Environment Variables** (user action required):
- Must remove compromised `GOOGLE_API_KEY`
- Must add new GCP service account credentials

---

## STEP 1: Update Railway Environment Variables (DO THIS FIRST!)

### Access Railway Dashboard

1. Go to: https://railway.app/dashboard
2. Find deployment: **web-production-e3796** (Text & Table Builder)
3. Click on the deployment
4. Navigate to: **Variables** tab

### Remove Compromised Key

**DELETE this environment variable immediately:**
```
GOOGLE_API_KEY  ← DELETE THIS
```

⚠️ **This will temporarily break the service** - that's GOOD for security!

### Add New Service Account Credentials

**ADD these three environment variables:**

```bash
# Your GCP project ID
GCP_PROJECT_ID=deckster-xyz

# GCP region
GCP_LOCATION=us-central1

# Service account JSON (paste the ENTIRE JSON content)
GCP_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"deckster-xyz",...PASTE FULL JSON HERE...}
```

### How to Get Service Account JSON

If you don't have the service account JSON yet:

1. Go to: https://console.cloud.google.com
2. Select project: **deckster-xyz** (or your new GCP project)
3. Navigate to: **IAM & Admin** → **Service Accounts**
4. Find your service account (or create one)
5. Click **Actions** (⋮) → **Manage Keys**
6. Click **Add Key** → **Create New Key** → **JSON**
7. Download the JSON file
8. Copy the ENTIRE contents and paste into `GCP_SERVICE_ACCOUNT_JSON`

**Important**: The JSON should start with `{"type":"service_account",...` and be one long line

---

## STEP 2: Deploy Updated Code to Railway

### Option A: Automatic Deployment (Recommended)

If Railway is connected to your Git repository, it will auto-deploy when you push:

```bash
# Navigate to Text Service directory
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.0

# Check what's changed
git status

# Stage the security fixes
git add app/core/llm_client.py requirements.txt SECURITY_UPDATE_VERTEX_AI.md RAILWAY_DEPLOYMENT_GUIDE.md

# Create commit with security message
git commit -m "🚨 SECURITY: Migrate from API key to Vertex AI service account auth

- Replace google.generativeai API key authentication with Vertex AI
- Implement service account credentials for secure Railway deployment
- Add google-cloud-aiplatform>=1.70.0 dependency
- Remove dependency on compromised GOOGLE_API_KEY environment variable
- Support both Railway (service account JSON) and local (ADC) authentication
- Fixes security vulnerability with compromised API key

Security Impact:
- Eliminates exposure to compromised API key AIzaSyAG2ruDJBZfFphdHZurk3X6vsXpmOkaH_c
- Implements least-privilege service account authentication
- Prevents unauthorized access and billing fraud"

# Push to trigger Railway deployment
git push origin main
```

Railway will automatically:
1. Detect the code changes
2. Install new dependencies from requirements.txt
3. Rebuild and redeploy the service
4. Use the new environment variables

### Option B: Manual Deployment via Railway CLI

If you have Railway CLI installed:

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.0

# Deploy to Railway
railway up
```

---

## STEP 3: Verify Deployment

### 3.1 Check Railway Deployment Logs

1. Go to Railway dashboard
2. Open **web-production-e3796** deployment
3. Click **Deployments** tab → select latest deployment
4. Click **View Logs**

**Look for these SUCCESS indicators:**
```
✓ Initialized Vertex AI with service account (project: deckster-xyz)
✓ Initialized Gemini model: gemini-2.5-flash
```

**Should NOT see:**
```
✗ GOOGLE_API_KEY (this should be completely gone)
✗ API key authentication errors
```

### 3.2 Test Health Endpoint

```bash
curl https://web-production-e3796.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "text-table-builder",
  "llm_provider": "gemini",
  "llm_model": "gemini-2.5-flash"
}
```

### 3.3 Test Text Generation API

```bash
curl -X POST https://web-production-e3796.up.railway.app/api/v1/generate/text \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["security update verification"],
    "narrative": "Testing Vertex AI authentication after security fix",
    "constraints": {"word_count": 50},
    "presentation_id": "security-test-001"
  }'
```

**Expected**: Should return generated text (NOT an authentication error)

**If you see errors**: Check Railway logs for specific error messages

### 3.4 Test from Director Agent (End-to-End)

From the Director Agent directory:

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/director_agent/v3.3

# Run full test with Stage 6 (Content Generation)
python3 tests/test_director_standalone.py --scenario default
```

**Expected**: All 6 stages should pass, including Stage 6 which calls the Text Service

---

## STEP 4: Security Verification Checklist

Before considering this update complete, verify:

### Railway Environment Variables
- [ ] Removed `GOOGLE_API_KEY` from Railway
- [ ] Added `GCP_PROJECT_ID=deckster-xyz`
- [ ] Added `GCP_LOCATION=us-central1`
- [ ] Added `GCP_SERVICE_ACCOUNT_JSON` with full JSON content

### Code Deployment
- [ ] Code changes committed to git
- [ ] Pushed to repository (triggered Railway deployment)
- [ ] Railway deployment succeeded (check logs)
- [ ] No build errors in Railway

### Functional Testing
- [ ] Health endpoint returns 200 OK
- [ ] Text generation API works
- [ ] Director Agent Stage 6 passes
- [ ] No authentication errors in logs
- [ ] Logs show "service account" authentication (not API key)

### Security Cleanup
- [ ] Old API key confirmed deleted from Railway
- [ ] Old API key confirmed deleted from GCP Console
- [ ] Old GCP project billing disabled (if applicable)
- [ ] No references to compromised key in logs
- [ ] No references to compromised key in codebase

---

## Rollback Plan (Emergency Only)

If something goes wrong and you need to rollback temporarily:

### Option 1: Fix Forward (Recommended)

1. Check Railway deployment logs for the specific error
2. Fix the issue in code
3. Commit and push to trigger new deployment

### Option 2: Revert Code (Last Resort)

```bash
# Revert to previous commit
git revert HEAD

# Push to trigger rollback deployment
git push origin main
```

**Note**: This will restore the compromised API key - only use in emergency!

---

## Timeline

**Estimated Time**: 15-30 minutes

1. **Step 1** (5-10 min): Update Railway environment variables
2. **Step 2** (5-10 min): Deploy code via git push
3. **Step 3** (5-10 min): Verify deployment and test
4. **Step 4** (5 min): Complete security checklist

---

## Troubleshooting

### Error: "GCP_PROJECT_ID environment variable required"

**Solution**: Add `GCP_PROJECT_ID=deckster-xyz` to Railway variables

### Error: "Failed to initialize Vertex AI"

**Solutions**:
1. Check that `GCP_SERVICE_ACCOUNT_JSON` is valid JSON
2. Verify the JSON starts with `{"type":"service_account"`
3. Ensure service account has "Vertex AI User" role in GCP IAM
4. Check Railway logs for specific error message

### Error: "Permission denied" or 403

**Solution**:
1. Go to GCP Console → IAM & Admin → IAM
2. Find your service account
3. Add role: **Vertex AI User**
4. Redeploy Railway service

### Health endpoint returns error

**Solutions**:
1. Check Railway deployment logs
2. Verify all environment variables are set
3. Ensure Railway deployment completed successfully
4. Try redeploying (Railway dashboard → Deployments → Redeploy)

### Director Agent Stage 6 fails

**Solutions**:
1. Verify Text Service health endpoint works
2. Check Director Agent's `.env` has correct `TEXT_SERVICE_URL`
3. Ensure no network/firewall issues
4. Check Railway logs for Text Service errors during the request

---

## Support

If you encounter issues:

1. **Check Railway Logs**: Most issues show clear error messages
2. **Verify Environment Variables**: Ensure all 3 new variables are set
3. **Check Service Account Permissions**: Ensure "Vertex AI User" role
4. **Test Health Endpoint**: Confirms basic service functionality
5. **Review SECURITY_UPDATE_VERTEX_AI.md**: Detailed technical reference

---

## Summary

This deployment guide walks through the critical security fix that:

✅ **Removes** compromised API key `AIzaSyAG2ruDJBZfFphdHZurk3X6vsXpmOkaH_c`
✅ **Implements** secure service account authentication via Vertex AI
✅ **Prevents** unauthorized access and billing fraud
✅ **Maintains** full functionality with enhanced security

**Status After Deployment**: 🔒 SECURE - Service account credentials, no API keys exposed

---

**Last Updated**: October 31, 2025
**Author**: Claude Code Security Team
