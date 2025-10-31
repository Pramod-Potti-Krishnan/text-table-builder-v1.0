# 🚨 CRITICAL SECURITY UPDATE: Migrate to Vertex AI Service Account Authentication

**Date**: October 31, 2025
**Priority**: URGENT
**Status**: Text Service currently using COMPROMISED API KEY

---

## ⚠️ Security Issue

The Text & Table Builder service deployed on Railway (`https://web-production-e3796.up.railway.app`) is **STILL USING** the compromised Google API key:
- **Compromised Key**: `AIzaSyAG2ruDJBZfFphdHZurk3X6vsXpmOkaH_c`
- **Risk**: Unauthorized access, billing fraud, data exposure
- **Action Required**: Immediate migration to service account authentication

---

## STEP 1: IMMEDIATE - Remove Compromised Key from Railway (DO THIS FIRST!)

### Access Railway Dashboard

1. Go to: https://railway.app/dashboard
2. Find deployment: **web-production-e3796** (Text & Table Builder)
3. Click on the deployment
4. Navigate to: **Variables** tab

### Remove Compromised Credentials

**DELETE** the following environment variable:
```
GOOGLE_API_KEY  ← DELETE THIS IMMEDIATELY
```

⚠️ **This will temporarily break the service, which is GOOD for security!**

---

## STEP 2: Add New Service Account Credentials to Railway

### In Railway Variables Tab, ADD:

```bash
# New GCP Project (deckster-xyz or your new project name)
GCP_PROJECT_ID=deckster-xyz

# GCP Region
GCP_LOCATION=us-central1

# Service Account JSON (paste the ENTIRE JSON content)
GCP_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...PASTE FULL JSON HERE..."}
```

### How to Get Service Account JSON:

1. Go to GCP Console: https://console.cloud.google.com
2. Navigate to: **IAM & Admin** → **Service Accounts**
3. Find your service account
4. Click **Actions** (three dots) → **Manage Keys**
5. Click **Add Key** → **Create New Key** → **JSON**
6. Download the JSON file
7. Copy the ENTIRE contents and paste into `GCP_SERVICE_ACCOUNT_JSON` in Railway

---

## STEP 3: Update Code - Replace GeminiClient with Vertex AI

### File: `app/core/llm_client.py`

**Find the GeminiClient class (lines 99-172) and REPLACE with:**

```python
class GeminiClient(BaseLLMClient):
    """
    Google Gemini LLM client using Vertex AI.

    v3.3 Security Update: Uses service account authentication instead of API keys.
    """

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        **kwargs
    ):
        super().__init__(model, **kwargs)

        # Import Vertex AI dependencies
        try:
            import vertexai
            from google.oauth2 import service_account
            from vertexai.preview.generative_models import GenerativeModel
        except ImportError:
            raise ImportError(
                "Vertex AI not installed. "
                "Install with: pip install google-cloud-aiplatform>=1.70.0"
            )

        # Initialize Vertex AI with service account credentials
        service_account_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")

        if not project_id:
            raise ValueError("GCP_PROJECT_ID environment variable required")

        try:
            if service_account_json:
                # Railway/Production: Use service account JSON from environment
                import json
                credentials_dict = json.loads(service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )

                vertexai.init(
                    project=project_id,
                    location=location,
                    credentials=credentials
                )
                logger.info(f"Initialized Vertex AI with service account (project: {project_id})")
            else:
                # Local development: Use Application Default Credentials
                vertexai.init(
                    project=project_id,
                    location=location
                )
                logger.info(f"Initialized Vertex AI with ADC (project: {project_id})")

            # Create Gemini model instance
            self.client = GenerativeModel(self.model)
            logger.info(f"Initialized Gemini model: {self.model}")

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise ValueError(f"Vertex AI initialization failed: {e}")

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate content using Gemini via Vertex AI."""
        start_time = time.time()

        try:
            # Gemini generation config
            from vertexai.preview.generative_models import GenerationConfig

            generation_config = GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )

            # Generate content
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract content and token usage
            content = response.text if hasattr(response, 'text') else str(response)

            # Token usage (if available)
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)

            return LLMResponse(
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                model=self.model,
                provider="gemini-vertex",
                latency_ms=latency_ms,
                finish_reason="",
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Gemini Vertex AI generation error: {e}")
            raise

    def is_configured(self) -> bool:
        """Check if Gemini Vertex AI is configured."""
        return os.getenv("GCP_PROJECT_ID") is not None
```

---

## STEP 4: Update Dependencies

### File: `requirements.txt`

**ADD** this line (or update version if already present):

```
google-cloud-aiplatform>=1.70.0
```

**KEEP** (still needed for compatibility):
```
google-generativeai>=0.3.0
```

---

## STEP 5: Deploy Updated Code to Railway

### Option A: Automatic Deployment (if connected to Git)

```bash
# From the text_table_builder/v1.0 directory
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.0

# Commit changes
git add app/core/llm_client.py requirements.txt SECURITY_UPDATE_VERTEX_AI.md
git commit -m "🚨 SECURITY: Migrate from API key to Vertex AI service account auth

- Replace google.generativeai API key authentication
- Implement Vertex AI with service account credentials
- Remove dependency on GOOGLE_API_KEY environment variable
- Add GCP_PROJECT_ID, GCP_LOCATION, GCP_SERVICE_ACCOUNT_JSON support
- Fixes compromised API key security issue"

# Push to Railway (triggers automatic deployment)
git push railway main
```

### Option B: Manual Deployment via Railway CLI

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.0

# Deploy to Railway
railway up
```

---

## STEP 6: Verify Deployment

### Test Health Endpoint

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

### Test Text Generation

```bash
curl -X POST https://web-production-e3796.up.railway.app/api/v1/generate/text \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["test security update"],
    "narrative": "Verifying Vertex AI authentication works",
    "constraints": {"word_count": 50},
    "presentation_id": "security-test-001"
  }'
```

**Expected**: Should return generated text (not an authentication error)

### Test from Director Agent

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/director_agent/v3.3

# Run test with Stage 6 enabled
python3 tests/test_director_standalone.py --scenario default
```

**Expected**: All 6 stages should pass, including Stage 6 (Content Generation)

---

## STEP 7: Verify Old Key is Disabled

### Check Railway Logs

1. Go to Railway dashboard
2. Open Text Service deployment
3. Check **Deployments** tab → **View Logs**
4. Look for:
   - ✅ "Initialized Vertex AI with service account"
   - ❌ NO "GOOGLE_API_KEY" references

### Verify Old Key Doesn't Work

The old compromised key should now be completely disabled and removed from:
- ✅ Railway environment variables
- ✅ Application code
- ✅ All configuration files

---

## Security Checklist

Before considering this update complete:

### ✅ Railway Environment Variables
- [ ] Removed `GOOGLE_API_KEY` from Railway
- [ ] Added `GCP_PROJECT_ID` to Railway
- [ ] Added `GCP_LOCATION` to Railway
- [ ] Added `GCP_SERVICE_ACCOUNT_JSON` to Railway

### ✅ Code Updates
- [ ] Updated `app/core/llm_client.py` GeminiClient class
- [ ] Updated `requirements.txt` with google-cloud-aiplatform
- [ ] Committed changes to git
- [ ] Pushed to Railway

### ✅ Testing
- [ ] Health endpoint returns 200 OK
- [ ] Text generation API works
- [ ] Director Agent Stage 6 passes
- [ ] No authentication errors in logs
- [ ] Logs show "service account" authentication (not API key)

### ✅ Cleanup
- [ ] Old API key confirmed deleted from Railway
- [ ] Old API key confirmed deleted from GCP Console
- [ ] Old GCP project billing disabled (if applicable)
- [ ] No references to compromised key in any logs

---

## Rollback Plan (If Something Goes Wrong)

If the update causes issues and you need to rollback temporarily:

### Option 1: Re-add API Key (ONLY if absolutely necessary for emergency)

**In Railway Variables:**
```
GOOGLE_API_KEY=<your-NEW-non-compromised-key>
```

Then redeploy the OLD code version.

### Option 2: Fix Forward

If there's an error in the new code:
1. Check Railway deployment logs for the specific error
2. Fix the code issue
3. Redeploy

---

## Timeline

**URGENT - Complete within 1-2 hours:**

1. ⏱️ **Step 1** (5 min): Remove old key from Railway
2. ⏱️ **Step 2** (5 min): Add service account to Railway
3. ⏱️ **Step 3** (15 min): Update code
4. ⏱️ **Step 4** (2 min): Update requirements.txt
5. ⏱️ **Step 5** (10 min): Deploy to Railway
6. ⏱️ **Step 6** (10 min): Test and verify
7. ⏱️ **Step 7** (5 min): Security verification

**Total Time**: ~52 minutes

---

## Support & Troubleshooting

### Common Issues

**Issue**: "GCP_PROJECT_ID environment variable required"
**Solution**: Ensure `GCP_PROJECT_ID` is set in Railway variables

**Issue**: "Failed to initialize Vertex AI"
**Solution**: Check that `GCP_SERVICE_ACCOUNT_JSON` is valid JSON and has correct permissions

**Issue**: "Permission denied" errors
**Solution**: Ensure service account has "Vertex AI User" role in GCP IAM

### Getting Help

If you encounter issues:
1. Check Railway deployment logs
2. Verify all environment variables are set correctly
3. Ensure service account has proper permissions
4. Test locally first if possible

---

## Summary

This update replaces the **compromised API key authentication** with **secure service account authentication** via Vertex AI, eliminating the security vulnerability and preventing unauthorized access.

**Status After Update**: ✅ SECURE - Using service account credentials, no API keys exposed

---

**Last Updated**: October 31, 2025
**Author**: Claude Code Security Update
