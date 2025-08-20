#!/usr/bin/env python3
"""
Simple test script to verify EdgeGrid credentials and debug API issues.
"""

import os
import sys
import requests

def load_env_file():
    """Load environment variables from akamai.env file."""
    env_file = os.path.join(os.path.dirname(__file__), 'akamai.env')
    if os.path.exists(env_file):
        print(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Loaded: {key}")
        return True
    else:
        print(f"Environment file not found: {env_file}")
        return False

def test_credentials():
    """Test EdgeGrid credentials and basic API connectivity."""
    
    # Load environment variables first
    if not load_env_file():
        print("Please create akamai.env file with your credentials")
        return False
    
    # Check environment variables
    host = os.environ.get("AKAMAI_HOST")
    client_token = os.environ.get("AKAMAI_CLIENT_TOKEN")
    client_secret = os.environ.get("AKAMAI_CLIENT_SECRET")
    access_token = os.environ.get("AKAMAI_ACCESS_TOKEN")
    account_switch_key = os.environ.get("AKAMAI_ACCOUNT_SWITCH_KEY")
    
    print("\n=== EdgeGrid Credentials Check ===")
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
        # Import EdgeGrid after environment is loaded
        from akamai.edgegrid import EdgeGridAuth
        
        # Create session with EdgeGrid auth
        session = requests.Session()
        session.auth = EdgeGridAuth(
            client_token=client_token,
            client_secret=client_secret,
            access_token=access_token,
        )
        
        # Test basic PAPI endpoint - first get contracts to find groupId
        print("Getting contracts to find required groupId...")
        contracts_url = f"https://{host}/papi/v1/contracts"
        contracts_response = session.get(contracts_url, timeout=30)
        
        if contracts_response.status_code != 200:
            print(f"❌ Failed to get contracts: {contracts_response.status_code}")
            print(f"Response: {contracts_response.text}")
            return False
        
        contracts_data = contracts_response.json()
        contracts = contracts_data.get("contracts", {}).get("items", [])
        
        if not contracts:
            print("❌ No contracts found")
            return False
        
        # Use the first contract
        contract = contracts[0]
        contract_id = contract.get("contractId")
        
        print(f"Using contract: {contract_id}")
        
        # Get groups for this contract
        print("Getting groups...")
        groups_url = f"https://{host}/papi/v1/groups"
        groups_response = session.get(groups_url, timeout=30)
        
        if groups_response.status_code != 200:
            print(f"❌ Failed to get groups: {groups_response.status_code}")
            print(f"Response: {groups_response.text}")
            return False
        
        groups_data = groups_response.json()
        groups = groups_data.get("groups", {}).get("items", [])
        
        if not groups:
            print("❌ No groups found")
            return False
        
        # Use the first group
        group = groups[0]
        group_id = group.get("groupId")
        
        print(f"Using group: {group_id}")
        
        # Now test properties endpoint with required parameters
        url = f"https://{host}/papi/v1/properties"
        params = {
            "contractId": contract_id,
            "groupId": group_id
        }
        if account_switch_key and account_switch_key != "your-account-switch-key-here":
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
            
    except ImportError:
        print("❌ Could not import EdgeGrid. Make sure you're in the virtual environment.")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Main function."""
    print("Akamai EdgeGrid Credentials Test (Simple Version)")
    print("=" * 50)
    
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
        print("Edit the akamai.env file with your actual values")

if __name__ == "__main__":
    main()
