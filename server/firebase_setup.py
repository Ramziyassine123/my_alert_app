#!/usr/bin/env python3
"""
Firebase Setup Script
This script helps set up Firebase configuration and verifies the setup
"""

import json
import shutil
from pathlib import Path


def main():
    print("=" * 60)
    print("Firebase Configuration Setup for ServerSide Project")
    print("=" * 60)

    # Define paths
    serverside_dir = Path("ServerSide")
    firebase_filename = "myalertappproject-firebase-adminsdk-fbsvc-4820c32a22.json"

    # Check if we're in the right directory
    if not serverside_dir.exists():
        print("❌ Error: ServerSide directory not found!")
        print("Please run this script from the parent directory containing both:")
        print("  - ServerSide/")
        print("  - my_alert_app/")
        return False

    # Look for the Firebase service account file
    firebase_source_path = None
    possible_locations = [
        Path(firebase_filename),  # Current directory
        Path("my_alert_app") / firebase_filename,  # my_alert_app directory
        serverside_dir / firebase_filename,  # ServerSide directory
    ]

    print("🔍 Looking for Firebase service account file...")
    for location in possible_locations:
        if location.exists():
            firebase_source_path = location
            print(f"✅ Found Firebase service account file at: {location}")
            break

    if not firebase_source_path:
        print("❌ Firebase service account file not found!")
        print(f"Please ensure '{firebase_filename}' exists in one of these locations:")
        for location in possible_locations:
            print(f"  - {location}")
        print("\nIf you have the file with a different name, please rename it to:")
        print(f"  {firebase_filename}")
        return False

    # Target location in ServerSide
    firebase_target_path = serverside_dir / firebase_filename

    # Copy file if needed
    if firebase_source_path != firebase_target_path:
        print(f"📋 Copying Firebase service account file to ServerSide...")
        try:
            shutil.copy2(firebase_source_path, firebase_target_path)
            print(f"✅ Copied to: {firebase_target_path}")
        except Exception as e:
            print(f"❌ Failed to copy file: {e}")
            return False
    else:
        print("✅ Firebase service account file already in correct location")

    # Verify the file content
    print("🔍 Verifying Firebase service account file...")
    try:
        with open(firebase_target_path, 'r') as f:
            firebase_config = json.load(f)

        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in firebase_config]

        if missing_fields:
            print(f"❌ Firebase service account file is missing required fields: {missing_fields}")
            return False

        print("✅ Firebase service account file is valid")
        print(f"   Project ID: {firebase_config.get('project_id')}")
        print(f"   Client Email: {firebase_config.get('client_email')}")

    except json.JSONDecodeError as e:
        print(f"❌ Firebase service account file contains invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading Firebase service account file: {e}")
        return False

    # Check ServerSide settings.py
    settings_path = serverside_dir / "settings.py"
    if settings_path.exists():
        print("🔍 Checking ServerSide settings.py...")
        with open(settings_path, 'r') as f:
            settings_content = f.read()

        if "FIREBASE_SERVICE_ACCOUNT_KEY" in settings_content:
            print("✅ FIREBASE_SERVICE_ACCOUNT_KEY found in settings.py")
        else:
            print("⚠️  FIREBASE_SERVICE_ACCOUNT_KEY not found in settings.py")
            print("   Please ensure the settings.py file includes the Firebase configuration")

    # Check if firebase-admin is installed
    print("🔍 Checking firebase-admin installation...")
    try:
        import firebase_admin
        print("✅ firebase-admin is installed")
    except ImportError:
        print("❌ firebase-admin is not installed")
        print("   Please install it with: pip install firebase-admin")
        return False

    print("\n" + "=" * 60)
    print("🎉 Firebase Setup Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Start the ServerSide server:")
    print("   cd ServerSide")
    print("   python manage.py runserver 8001")
    print("")
    print("2. Start the my_alert_app client:")
    print("   cd my_alert_app")
    print("   python manage.py runserver 8000")
    print("")
    print("3. Access the test dashboard:")
    print("   http://127.0.0.1:8000/test/")
    print("")
    print("The Firebase push notifications should now work correctly!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    main()
