#!/usr/bin/env python
"""
Enhanced Firebase Token Cleanup Script
Place this file in: ServerSide/cleanup_firebase_tokens.py
Run with: cd ServerSide && python cleanup_firebase_tokens.py
"""

import os
import sys
import django

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ServerSide.settings')

try:
    django.setup()
    from push.models import FCMToken
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    print("Make sure you're running this from the ServerSide directory")
    print("Usage: cd ServerSide && python cleanup_firebase_tokens.py")
    sys.exit(1)


def cleanup_invalid_tokens():
    """Remove invalid Firebase tokens from database"""
    print("🧹 Starting Enhanced Firebase token cleanup...")
    print("=" * 50)

    # Get initial count
    initial_count = FCMToken.objects.count()
    print(f"📊 Initial tokens in database: {initial_count}")

    if initial_count == 0:
        print("✅ No tokens to clean up!")
        return

    deleted_counts = {}

    # Remove test tokens
    test_tokens = FCMToken.objects.filter(token__startswith='test_token_')
    deleted_counts['test_tokens'] = test_tokens.count()
    if deleted_counts['test_tokens'] > 0:
        test_tokens.delete()
        print(f"🗑️  Deleted {deleted_counts['test_tokens']} test tokens")

    # Remove fake tokens
    fake_tokens = FCMToken.objects.filter(token__startswith='faketoken_')
    deleted_counts['fake_tokens'] = fake_tokens.count()
    if deleted_counts['fake_tokens'] > 0:
        fake_tokens.delete()
        print(f"🗑️  Deleted {deleted_counts['fake_tokens']} fake tokens")

    # Remove enhanced test tokens
    enhanced_tokens = FCMToken.objects.filter(token__contains='enhanced_test')
    deleted_counts['enhanced_tokens'] = enhanced_tokens.count()
    if deleted_counts['enhanced_tokens'] > 0:
        enhanced_tokens.delete()
        print(f"🗑️  Deleted {deleted_counts['enhanced_tokens']} enhanced test tokens")

    # Remove tokens with realistic test patterns
    realistic_test_tokens = FCMToken.objects.filter(token__contains='dGVzdF90b2tlbl8')
    deleted_counts['realistic_test'] = realistic_test_tokens.count()
    if deleted_counts['realistic_test'] > 0:
        realistic_test_tokens.delete()
        print(f"🗑️  Deleted {deleted_counts['realistic_test']} realistic test tokens")

    # Remove suspiciously short tokens (real FCM tokens are usually 152+ chars)
    # Use Python filtering since Django doesn't support length lookup on CharField
    all_tokens = FCMToken.objects.all()
    short_token_ids = [token.id for token in all_tokens if len(token.token) < 100]
    short_tokens = FCMToken.objects.filter(id__in=short_token_ids)
    deleted_counts['short_tokens'] = short_tokens.count()
    if deleted_counts['short_tokens'] > 0:
        short_tokens.delete()
        print(f"🗑️  Deleted {deleted_counts['short_tokens']} suspiciously short tokens")

    # Remove tokens with obvious test patterns (case insensitive)
    # Use Python filtering for length check
    all_remaining_tokens = FCMToken.objects.filter(token__icontains='test')
    obvious_test_ids = [token.id for token in all_remaining_tokens if len(token.token) <= 140]
    obvious_test = FCMToken.objects.filter(id__in=obvious_test_ids)
    deleted_counts['obvious_test'] = obvious_test.count()
    if deleted_counts['obvious_test'] > 0:
        obvious_test.delete()
        print(f"🗑️  Deleted {deleted_counts['obvious_test']} obvious test tokens")

    # Remove tokens containing 'demo' or 'sample'
    demo_tokens = FCMToken.objects.filter(
        token__icontains='demo'
    ) | FCMToken.objects.filter(
        token__icontains='sample'
    )
    deleted_counts['demo_tokens'] = demo_tokens.count()
    if deleted_counts['demo_tokens'] > 0:
        demo_tokens.delete()
        print(f"🗑️  Deleted {deleted_counts['demo_tokens']} demo/sample tokens")

    # Final count
    final_count = FCMToken.objects.count()
    total_deleted = initial_count - final_count

    print("=" * 50)
    print(f"✅ Cleanup complete!")
    print(f"📊 Total tokens deleted: {total_deleted}")
    print(f"📊 Remaining tokens: {final_count}")

    # Show breakdown
    if total_deleted > 0:
        print(f"\n📋 Deletion breakdown:")
        for category, count in deleted_counts.items():
            if count > 0:
                print(f"   • {category.replace('_', ' ').title()}: {count}")

    # Show remaining tokens (first 50 chars for security)
    if final_count > 0:
        print(f"\n📋 Remaining tokens:")
        for i, token in enumerate(FCMToken.objects.all()[:10], 1):
            token_preview = token.token[:50] + "..." if len(token.token) > 50 else token.token
            active_status = "✅ Active" if token.is_active else "❌ Inactive"
            print(f"   {i}. {token_preview} (length: {len(token.token)}) - {active_status}")

        if final_count > 10:
            print(f"   ... and {final_count - 10} more tokens")
    else:
        print("\n⚠️  No tokens remaining! You'll need real devices to register new tokens.")


def validate_remaining_tokens():
    """Validate that remaining tokens look like real FCM tokens"""
    print(f"\n🔍 Validating remaining tokens...")

    valid_tokens = 0
    suspicious_tokens = 0
    inactive_tokens = 0

    for token in FCMToken.objects.all():
        if not token.is_active:
            inactive_tokens += 1
            continue

        # Real FCM tokens are typically 152+ characters, alphanumeric with some special chars
        if (len(token.token) >= 140 and
                not any(test_word in token.token.lower() for test_word in ['test', 'fake', 'demo', 'enhanced', 'sample'])):
            valid_tokens += 1
        else:
            suspicious_tokens += 1
            print(f"⚠️  Suspicious token: {token.token[:30]}... (length: {len(token.token)})")

    print(f"✅ Valid-looking tokens: {valid_tokens}")
    print(f"⚠️  Suspicious tokens: {suspicious_tokens}")
    print(f"❌ Inactive tokens: {inactive_tokens}")


def show_next_steps():
    """Show what to do next"""
    print(f"\n🚀 Next Steps:")
    print(f"=" * 30)
    print(f"1. Start your Django server:")
    print(f"   cd ServerSide && python manage.py runserver 8001")
    print(f"")
    print(f"2. Test push notifications:")
    print(f"   Open: http://localhost:8001/alerts/push/")
    print(f"   Click 'Enable Notifications' on a real device")
    print(f"")
    print(f"3. Send test notification:")
    print(f"   Use the 'Send Sequential Alerts' button")
    print(f"")
    print(f"4. Monitor logs:")
    print(f"   Should see much fewer '260 failed' errors")
    print(f"")
    print(f"5. If issues persist:")
    print(f"   • Check Firebase project configuration")
    print(f"   • Verify VAPID key in settings")
    print(f"   • Test with real mobile devices")


if __name__ == "__main__":
    print("Firebase Token Cleanup Utility")
    print("=" * 50)

    try:
        cleanup_invalid_tokens()
        validate_remaining_tokens()
        show_next_steps()

        print(f"\n🎉 Cleanup completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        print(f"Make sure you're in the ServerSide directory and Django is properly set up")
        sys.exit(1)
