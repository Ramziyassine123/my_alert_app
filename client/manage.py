#!/usr/bin/env python
"""Django's command-line utility for my_alert_app performance testing client."""
import os
import sys


def main():
    """Run administrative tasks for performance testing client."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_alert_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Print client info on runserver
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print("=" * 60)
        print("📊 Starting Performance Testing Dashboard Client")
        print("=" * 60)
        print("Dashboard: http://127.0.0.1:8000")
        print("Testing Server: http://127.0.0.1:8001")
        print("=" * 60)
        print("⚠️  Make sure ServerSide server is running on port 8001!")
        print("=" * 60)

        # Add port if not specified
        if len(sys.argv) == 2:
            sys.argv.append('8000')

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
