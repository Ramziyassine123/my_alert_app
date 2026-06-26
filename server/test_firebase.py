# Create a test file: test_firebase.py in ServerSide directory
import requests

base_url = "http://127.0.0.1:8001/api/push"

# Test 1: Base endpoint
try:
    response = requests.get(f"{base_url}/")
    print(f"✅ Base endpoint: {response.status_code}")
    if response.text:
        print(response.json())
except Exception as e:
    print(f"❌ Base endpoint error: {e}")

# Test 2: Stats endpoint
try:
    response = requests.get(f"{base_url}/stats/")
    print(f"✅ Stats endpoint: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"❌ Stats endpoint error: {e}")

# Test 3: Send-sequential endpoint
try:
    response = requests.post(f"{base_url}/send-sequential/",
                             json={"delay": 1.0})
    print(f"✅ Send-sequential: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"❌ Send-sequential error: {e}")
