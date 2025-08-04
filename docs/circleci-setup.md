# CircleCI Setup for Gmail Integration & E2E Tests

This guide explains how to securely run Gmail integration and E2E tests on CircleCI using environment variables.

## 🔐 **Security Overview**

Gmail tests require OAuth2 credentials and tokens. **Never commit these to git**. Instead, we:
1. Store credentials as CircleCI environment variables 
2. Generate token files from environment variables during CI runs
3. Use different workflows for different test types

## 📋 **Prerequisites**

Before setting up CircleCI, you need:

1. **Gmail API credentials** (`credentials.json`)
2. **Valid OAuth2 token** (generated locally first)
3. **CircleCI project** connected to your repository

## 🚀 **Setup Steps**

### **Step 1: Generate Local Credentials**

First, get your Gmail integration working locally:

```bash
# 1. Set up Gmail API credentials (if not done)
# - Go to Google Cloud Console
# - Enable Gmail API  
# - Create OAuth2 Desktop Application credentials
# - Download as credentials.json

# 2. Test locally to generate tokens
uv run pytest tests/integration/ -v --tb=short
uv run pytest tests/e2e/ -v --tb=short
```

This creates `test_token.json` and `e2e_token.json` files.

### **Step 2: Prepare Environment Variables**

```bash
# Get your credentials file content
cat credentials.json

# Get your token files content (these contain refresh tokens)
cat test_token.json  # For integration tests
cat e2e_token.json   # For E2E tests
```

### **Step 3: Set CircleCI Environment Variables**

Go to your CircleCI project settings → Environment Variables and add:

#### **Required Variables:**

| Variable Name | Value | Description |
|---------------|--------|-------------|
| `GMAIL_CREDENTIALS_JSON` | `{"installed":{"client_id":"...","client_secret":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","redirect_uris":["..."]}}` | Contents of `credentials.json` file |

#### **Optional Variables (for pre-authorized tokens):**

| Variable Name | Value | Description |
|---------------|--------|-------------|
| `GMAIL_CI_TOKEN_JSON` | `{"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":["..."],"expiry":"..."}` | Contents of `test_token.json` for integration tests |
| `GMAIL_E2E_TOKEN_JSON` | `{"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":["..."],"expiry":"..."}` | Contents of `e2e_token.json` for E2E tests |

### **Step 4: Understanding Test Workflows**

The CircleCI configuration includes multiple workflows:

#### **1. Quick PR Check** (Default)
- Runs on all PRs
- Only unit tests (no Gmail API calls)
- Fast feedback for contributors

#### **2. Full Test Suite** 
- Runs on `main`/`develop` branches
- Includes integration and E2E tests
- Requires Gmail credentials

#### **3. Feature Branch Testing**
- Integration tests: branches matching `/feature\/.*integration.*/`
- E2E tests: branches matching `/feature\/.*e2e.*/`

## 🔧 **CircleCI Configuration Details**

### **Jobs Overview:**

1. **`lint`** - Code quality checks (ruff, mypy)
2. **`test-unit`** - Unit tests for all components
3. **`test-integration`** - Gmail API integration tests
4. **`test-e2e`** - End-to-end workflow tests  
5. **`build`** - Build distributable packages

### **Environment Variable Usage:**

```yaml
# In CircleCI, credentials are injected like this:
- run:
    name: Setup Gmail credentials
    command: |
      echo "$GMAIL_CREDENTIALS_JSON" > credentials.json
      if [ ! -z "$GMAIL_CI_TOKEN_JSON" ]; then
        echo "$GMAIL_CI_TOKEN_JSON" > ci_token.json
      fi
```

## 🧪 **Testing Strategies**

### **Option A: Pre-authorized Tokens (Recommended)**
- Set up `GMAIL_CI_TOKEN_JSON` and `GMAIL_E2E_TOKEN_JSON`
- Tests use existing refresh tokens
- No browser interaction needed
- Most reliable for CI

### **Option B: Fresh OAuth Flow**
- Only set `GMAIL_CREDENTIALS_JSON`
- Tests generate new tokens each run
- May require user interaction (not ideal for CI)
- Better for testing full auth flow

### **Option C: Conditional Testing**
- Set environment variables only for specific branches
- Use CircleCI contexts for sensitive projects
- Enable/disable Gmail tests based on availability

## 🚦 **Running Tests**

### **Trigger Integration Tests:**
```bash
# Push to feature branch with "integration" in name
git checkout -b feature/gmail-integration-improvements
git push origin feature/gmail-integration-improvements
```

### **Trigger E2E Tests:**
```bash
# Push to feature branch with "e2e" in name  
git checkout -b feature/e2e-workflow-testing
git push origin feature/e2e-workflow-testing
```

### **Trigger Full Test Suite:**
```bash
# Push to main or develop
git checkout main
git push origin main
```

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **"Gmail credentials not available"**
- Check `GMAIL_CREDENTIALS_JSON` is set correctly
- Ensure JSON is valid (use online JSON validator)
- Verify credentials file format matches Google's structure

#### **"Authentication failed"**
- Check if credentials are expired
- Verify OAuth2 application is enabled in Google Cloud Console
- Ensure Gmail API is enabled for your project

#### **"Token refresh failed"**
- Regenerate tokens locally and update environment variables
- Check if refresh_token is included in token JSON
- Verify token hasn't been revoked

#### **"Rate limiting"**
- Gmail API has quotas and rate limits
- Add delays between requests if needed
- Use smaller test datasets

### **Debug Commands:**

```bash
# Test locally with same environment setup
export GMAIL_CREDENTIALS_JSON='{"installed":{...}}'
export GMAIL_CI_TOKEN_JSON='{"token":...}'

# Run specific test types
uv run pytest tests/integration/ -v -k "test_config_and_connection"
uv run pytest tests/e2e/ -v -k "test_complete_email_reading"

# Check token validity
python -c "
import json
import os
token = json.loads(os.environ['GMAIL_CI_TOKEN_JSON'])
print('Token expires:', token.get('expiry', 'No expiry'))
print('Has refresh token:', 'refresh_token' in token)
"
```

## 🔒 **Security Best Practices**

1. **Never commit credentials/tokens to git**
2. **Use CircleCI contexts for sensitive projects**
3. **Rotate credentials regularly**
4. **Limit OAuth2 scopes to minimum required**
5. **Monitor for suspicious API usage**
6. **Use separate Google projects for CI vs production**

## 📊 **Workflow Examples**

### **Development Workflow:**
```bash
# 1. Feature development (unit tests only)
git checkout -b feature/new-email-parser
git push origin feature/new-email-parser
# → Runs lint + unit tests

# 2. Integration testing
git checkout -b feature/new-email-parser-integration  
git push origin feature/new-email-parser-integration
# → Runs lint + unit + integration tests

# 3. Full testing before merge
git checkout main
git merge feature/new-email-parser-integration
git push origin main
# → Runs complete test suite including E2E
```

### **Emergency Fixes:**
```bash
# Skip Gmail tests for urgent fixes
git checkout -b hotfix/critical-security-fix
git push origin hotfix/critical-security-fix
# → Only runs unit tests (fast)
```

---

## 📞 **Support**

If you encounter issues:
1. Check CircleCI build logs for specific error messages
2. Verify environment variables are set correctly
3. Test Gmail API access manually with same credentials
4. Review Google Cloud Console for API quotas/limits 