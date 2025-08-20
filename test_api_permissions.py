#!/usr/bin/env python3
"""
Test script to check which Akamai APIs your credentials have access to.
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

def test_api_endpoint(session, host, endpoint, description):
    """Test a specific API endpoint."""
    url = f"https://{host}{endpoint}"
    print(f"\n--- Testing {description} ---")
    print(f"URL: {url}")
    
    try:
        response = session.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS: {description}")
            return True
        elif response.status_code == 403:
            print(f"❌ FORBIDDEN: No permission for {description}")
            return False
        elif response.status_code == 400:
            print(f"⚠️  BAD REQUEST: {description} - might need parameters")
            return False
        else:
            print(f"❌ FAILED: {description} - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {description} - {e}")
        return False

def test_api_permissions():
    """Test various Akamai API endpoints to see which ones are accessible."""
    
    # Load environment variables first
    if not load_env_file():
        print("Please create akamai.env file with your credentials")
        return False
    
    # Check environment variables
    host = os.environ.get("AKAMAI_HOST")
    client_token = os.environ.get("AKAMAI_CLIENT_TOKEN")
    client_secret = os.environ.get("AKAMAI_CLIENT_SECRET")
    access_token = os.environ.get("AKAMAI_ACCESS_TOKEN")
    
    if not all([host, client_token, client_secret, access_token]):
        print("❌ Missing required credentials!")
        return False
    
    print(f"\nHost: {host}")
    
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
        
        print("\n=== Testing API Permissions ===")
        
        # Test various Akamai APIs
        apis_to_test = [
            ("/papi/v1/contracts", "Contracts API"),
            ("/papi/v1/groups", "Groups API"),
            ("/papi/v1/properties", "Properties API (PAPI)"),
            ("/cps/v2/enrollments", "Certificate Provisioning System (CPS)"),
            ("/appsec/v1/configs", "Application Security (AppSec)"),
            ("/gtm/v1/domains", "Global Traffic Management (GTM)"),
            ("/edgedns/v1/zones", "Edge DNS"),
            ("/edgeworkers/v1/ids", "EdgeWorkers"),
            ("/cloudlets/v2/policies", "Cloudlets"),
            ("/cloud-wrapper/v1/locations", "Cloud Wrapper"),
        ]
        
        results = {}
        for endpoint, description in apis_to_test:
            results[description] = test_api_endpoint(session, host, endpoint, description)
        
        # Summary
        print("\n=== API Access Summary ===")
        accessible_apis = [desc for desc, result in results.items() if result]
        forbidden_apis = [desc for desc, result in results.items() if not result]
        
        if accessible_apis:
            print("✅ ACCESSIBLE APIs:")
            for api in accessible_apis:
                print(f"  • {api}")
        
        if forbidden_apis:
            print("\n❌ FORBIDDEN APIs (need permissions):")
            for api in forbidden_apis:
                print(f"  • {api}")
        
        print(f"\nTotal: {len(accessible_apis)} accessible, {len(forbidden_apis)} forbidden")
        
        return len(accessible_apis) > 0
        
    except ImportError:
        print("❌ Could not import EdgeGrid. Make sure you're in the virtual environment.")
        return False
    except Exception as e:
        print(f"❌ Error testing APIs: {e}")
        return False

def main():
    """Main function."""
    print("Akamai API Permissions Test")
    print("=" * 40)
    
    if test_api_permissions():
        print("\n🎉 Some APIs are accessible!")
        print("Check the summary above to see which ones work.")
    else:
        print("\n💥 No APIs are accessible.")
        print("Please check your API client permissions in Akamai Control Center.")

if __name__ == "__main__":
    main()
