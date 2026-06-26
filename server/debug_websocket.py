#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ServerSide.settings')
django.setup()

import websocket
import json
import time
import uuid

def debug_websocket_ping():
    """Debug WebSocket ping/pong responses"""

    # Try different WebSocket URLs
    urls_to_try = [
        "ws://localhost:8001/ws/alerts/",
        "ws://localhost:8000/ws/alerts/",
        "ws://127.0.0.1:8001/ws/alerts/",
        "ws://127.0.0.1:8000/ws/alerts/"
    ]

    for url in urls_to_try:
        print(f"\n🔗 Trying to connect to: {url}")
        try:
            ws = websocket.create_connection(url, timeout=5)
            print("✅ Connected!")
            break
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    else:
        print("❌ Could not connect to any WebSocket URL")
        return

    # Send 3 test pings
    for i in range(3):
        ping_id = str(uuid.uuid4())
        send_time = time.time() * 1000

        ping_message = {
            'type': 'ping',
            'ping_id': ping_id,
            'timestamp': send_time,
            'sequence': i,
            'client_id': 'debug_client'
        }

        print(f"\n📤 Sending ping {i+1}:")
        print(f"   Ping ID: {ping_id}")
        print(f"   Full message: {json.dumps(ping_message)}")

        try:
            # Send ping
            ws.send(json.dumps(ping_message))
            print("   ✅ Ping sent successfully")

            # Wait for response
            ws.settimeout(5)
            response = ws.recv()
            receive_time = time.time() * 1000

            print(f"\n📥 Received response:")
            print(f"   Raw response: {response}")
            print(f"   Response length: {len(response)} characters")

            # Try to parse JSON
            try:
                data = json.loads(response)
                print(f"   ✅ JSON parsed successfully:")
                print(f"   Response type: '{data.get('type')}'")
                print(f"   Response ping_id: '{data.get('ping_id')}'")
                print(f"   All keys in response: {list(data.keys())}")

                # Check if it's a proper pong
                if data.get('type') == 'pong':
                    if data.get('ping_id') == ping_id:
                        latency = receive_time - send_time
                        print(f"   🎉 PERFECT PING/PONG! Latency: {latency:.2f}ms")
                    else:
                        print(f"   ⚠️  Pong type correct, but ping_id mismatch:")
                        print(f"      Sent: '{ping_id}'")
                        print(f"      Received: '{data.get('ping_id')}'")
                else:
                    print(f"   ❌ Wrong response type. Expected 'pong', got '{data.get('type')}'")

            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parsing failed: {e}")
                print(f"   This means the server sent invalid JSON")

        except websocket.WebSocketTimeoutException:
            print(f"   ⏰ Timeout - no response received within 5 seconds")
        except Exception as e:
            print(f"   ❌ Error during ping test: {e}")

        time.sleep(0.5)

    ws.close()
    print("\n🔚 Debug test completed!")

if __name__ == "__main__":
    debug_websocket_ping()
