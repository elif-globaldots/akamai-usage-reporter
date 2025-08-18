#!/usr/bin/env python3
"""
Test script to verify EdgeGrid credentials and debug API issues.
"""

import os
import sys
import requests
from akamai.edgegrid import EdgeGridAuth

def test_credentials():
    """Test EdgeGrid credentials and basic API connectivity."""
    
    # Check environment variables
    host = os.environ.get("AKAMAI_HOST")
    client_token = os.environ.get("AKAMAI_CLIENT_TOKEN")
    client_secret = os.environ.get("AKAMAI_CLIENT_SECRET")
    access_token = os.environ.get("AKAMAI_ACCESS_TOKEN")
    account_switch_key = os.environ.get("AKAMAI_ACCOUNT_SWITCH_KEY")
    
    print("=== EdgeGrid Credentials Check ===")
    print(f"AKAMAI_HOST: {'✓ Set' if host else '✗ Missing'}")
    print(f"AKAMAI_CLIENT_TOKEN: {'✓ Set' if client_token else '✗ Missing'}")
    print(f"AKAMAI_CLIENT_SECRET: {'✓ Set' if client_secret else '✗ Missing'}")
    print(f"AKAMAI_ACCESS_TOKEN: {'✓ Set' if access_token else '✗ Missing'}")
    print(f"AKAMAI_ACCOUNT_SWITCH_KEY: {'✓ Set' if account_switch_key else '✗ Not set (optional)'}")
    
    if not all([host, client_token, client_secret, access_token]):
        print("\n❌ Missing required credentials!")
        return False
    
    print(f"\nHost: {host}")
    print(f"Client Token: {client_token[:8]}...")
    print(f"Access Token: {access_token[:8]}...")
    
    # Test basic connectivity
    print("\n=== Testing API Connectivity ===")
    
    try:
        # Create session with EdgeGrid auth
        session = requests.Session()
        session.auth = EdgeGridAuth(
            client_token=client_token,
            client_secret=client_secret,
            access_token=access_token,
        )
        
        # Test basic PAPI endpoint
        url = f"https://{host}/papi/v1/properties"
        params = {}
        if account_switch_key:
            params["accountSwitchKey"] = account_switch_key
        
        print(f"Testing URL: {url}")
        print(f"Params: {params}")
        
        response = session.get(url, params=params, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API call successful!")
            print(f"Properties found: {len(data.get('properties', {}).get('items', []))}")
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Main function."""
    print("Akamai EdgeGrid Credentials Test")
    print("=" * 40)
    
    if test_credentials():
        print("\n🎉 Credentials are working! You can now run the main script.")
    else:
        print("\n💥 Credentials test failed. Please check your setup.")
        print("\nCommon issues:")
        print("1. Missing environment variables")
        print("2. Incorrect host format (should start with 'akab-')")
        print("3. Invalid tokens or expired access")
        print("4. Network connectivity issues")
        print("5. Account permissions")
        
        print("\nTo set credentials:")
        print("export AKAMAI_HOST='your-host.akamaiapis.net'")
        print("export AKAMAI_CLIENT_TOKEN='your-client-token'")
        print("export AKAMAI_CLIENT_SECRET='your-client-secret'")
        print("export AKAMAI_ACCESS_TOKEN='your-access-token'")
        print("export AKAMAI_ACCOUNT_SWITCH_KEY='your-account-switch-key'  # Optional")

if __name__ == "__main__":
    main()
