#!/usr/bin/env python3
"""
Detailed debug script for PAPI issues.
"""

import os
import sys
import requests
import json

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

def debug_papi_calls():
    """Debug PAPI calls step by step."""
    
    if not load_env_file():
        return False
    
    host = os.environ.get("AKAMAI_HOST")
    client_token = os.environ.get("AKAMAI_CLIENT_TOKEN")
    client_secret = os.environ.get("AKAMAI_CLIENT_SECRET")
    access_token = os.environ.get("AKAMAI_ACCESS_TOKEN")
    
    if not all([host, client_token, client_secret, access_token]):
        print("❌ Missing credentials!")
        return False
    
    print(f"\nHost: {host}")
    print(f"Client Token: {client_token[:8]}...")
    print(f"Access Token: {access_token[:8]}...")
    
    try:
        from akamai.edgegrid import EdgeGridAuth
        
        session = requests.Session()
        session.auth = EdgeGridAuth(
            client_token=client_token,
            client_secret=client_secret,
            access_token=access_token,
        )
        
        print("\n=== Step 1: Test Contracts API ===")
        contracts_url = f"https://{host}/papi/v1/contracts"
        print(f"URL: {contracts_url}")
        
        response = session.get(contracts_url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            contracts_data = response.json()
            contracts = contracts_data.get("contracts", {}).get("items", [])
            print(f"✓ Found {len(contracts)} contracts")
            
            if contracts:
                contract = contracts[0]
                contract_id = contract.get("contractId")
                print(f"First contract: {contract_id}")
                print(f"Contract details: {json.dumps(contract, indent=2)}")
                
                print("\n=== Step 2: Test Groups API ===")
                groups_url = f"https://{host}/papi/v1/groups"
                print(f"URL: {groups_url}")
                
                groups_response = session.get(groups_url, timeout=30)
                print(f"Status: {groups_response.status_code}")
                
                if groups_response.status_code == 200:
                    groups_data = groups_response.json()
                    groups = groups_data.get("groups", {}).get("items", [])
                    print(f"✓ Found {len(groups)} groups")
                    
                    if groups:
                        group = groups[0]
                        group_id = group.get("groupId")
                        print(f"First group: {group_id}")
                        print(f"Group details: {json.dumps(group, indent=2)}")
                        
                        print("\n=== Step 3: Test Properties API with Parameters ===")
                        properties_url = f"https://{host}/papi/v1/properties"
                        params = {
                            "contractId": contract_id,
                            "groupId": group_id
                        }
                        print(f"URL: {properties_url}")
                        print(f"Params: {params}")
                        
                        properties_response = session.get(properties_url, params=params, timeout=30)
                        print(f"Status: {properties_response.status_code}")
                        print(f"Response Headers: {dict(properties_response.headers)}")
                        
                        if properties_response.status_code == 200:
                            properties_data = properties_response.json()
                            properties = properties_data.get("properties", {}).get("items", [])
                            print(f"✓ SUCCESS! Found {len(properties)} properties")
                            return True
                        else:
                            print(f"❌ Properties API failed: {properties_response.status_code}")
                            print(f"Response: {properties_response.text}")
                            
                            # Try without parameters
                            print("\n=== Step 4: Test Properties API WITHOUT Parameters ===")
                            properties_response2 = session.get(properties_url, timeout=30)
                            print(f"Status: {properties_response2.status_code}")
                            print(f"Response: {properties_response2.text}")
                            
                            return False
                    else:
                        print("❌ No groups found")
                        return False
                else:
                    print(f"❌ Groups API failed: {groups_response.status_code}")
                    print(f"Response: {groups_response.text}")
                    return False
            else:
                print("❌ No contracts found")
                return False
        else:
            print(f"❌ Contracts API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("PAPI Debug Script")
    print("=" * 30)
    
    if debug_papi_calls():
        print("\n🎉 PAPI is working! The issue might be elsewhere.")
    else:
        print("\n💥 PAPI is still failing. Let's check other possibilities.")
        print("\nPossible issues:")
        print("1. API client scope restrictions")
        print("2. Network/firewall issues")
        print("3. Akamai account configuration")
        print("4. API version compatibility")

if __name__ == "__main__":
    main()
