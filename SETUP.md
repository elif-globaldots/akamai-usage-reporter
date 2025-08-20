# Akamai Usage Reporter Setup Guide

## Quick Start

### 1. Set Environment Variables (Recommended Method)

**Option A: Use the akamai.env file (Easiest)**
```bash
# Edit the akamai.env file with your credentials
cp akamai.env.example akamai.env
# Then edit akamai.env with your actual values
```

**Option B: Export in terminal (Alternative)**
```bash
# Required credentials
export AKAMAI_HOST="your-host.akamaiapis.net"
export AKAMAI_CLIENT_TOKEN="your-client-token"
export AKAMAI_CLIENT_SECRET="your-client-secret"
export AKAMAI_ACCESS_TOKEN="your-access-token"

# Optional: Account switch key (if you have multiple accounts)
export AKAMAI_ACCOUNT_SWITCH_KEY="your-account-switch-key"
```

### 2. Test Your Credentials

```bash
# The script will automatically load the virtual environment and akamai.env file
python3 test_credentials.py
```

### 3. Run the Main Script

```bash
# The script will automatically load the virtual environment and akamai.env file
python3 -m akamai_usage_reporter --out-dir ./out --include-rules --include-products
```

## Troubleshooting

### Common Error: HTTP 400 Bad Request

This usually means one of these issues:

1. **Missing or incorrect credentials**
   - Check all environment variables are set
   - Verify tokens are correct and not expired

2. **Wrong host format**
   - Should start with `akab-` (e.g., `akab-ci6smccddm65vh2m-kmlfdngpberpgldx.luna.akamaiapis.net`)

3. **Permission issues**
   - Your API client might not have access to PAPI
   - Check with your Akamai administrator

4. **Account switch key**
   - Wrong or missing account switch key
   - Try without it first

### Debug Mode

Use the `--debug` flag for detailed error information:

```bash
python3 -m akamai_usage_reporter --debug --out-dir ./out --include-rules --include-products
```

### SSL Warnings

If you see SSL warnings about LibreSSL, they're usually harmless but can be fixed by:

```bash
# Install OpenSSL via Homebrew
brew install openssl

# Or upgrade urllib3
pip install --upgrade urllib3
```

## Getting Your Credentials

1. **Go to Akamai Control Center**
2. **Navigate to Admin → API → API Credentials**
3. **Create a new API client** with these permissions:
   - Property Manager (PAPI)
   - Certificate Provisioning System (CPS)
   - Application Security (AppSec)
   - Global Traffic Management (GTM)
   - Edge DNS
   - EdgeWorkers
   - Cloudlets
   - Cloud Wrapper

4. **Download the credentials** and set them as environment variables

## Auto-Loading Features

The script now automatically:

1. **Loads the virtual environment** - No need to manually activate `.venv`
2. **Loads credentials from `akamai.env`** - No need to export variables manually
3. **Provides detailed feedback** - Shows what's being loaded

## Example akamai.env file

Edit the `akamai.env` file in your project directory:

```bash
AKAMAI_HOST=akab-ci6smccddm65vh2m-kmlfdngpberpgldx.luna.akamaiapis.net
AKAMAI_CLIENT_TOKEN=akab-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AKAMAI_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AKAMAI_ACCESS_TOKEN=akab-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AKAMAI_ACCOUNT_SWITCH_KEY=1-xxxxxxxx
```

**No need to source it manually** - the script loads it automatically!

## Still Having Issues?

1. **Run the test script first**: `python3 test_credentials.py`
2. **Check the debug output**: Use `--debug` flag
3. **Verify network connectivity**: Can you reach the Akamai host?
4. **Check with Akamai support**: Your account might have restrictions
