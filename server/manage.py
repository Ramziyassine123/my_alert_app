#!/usr/bin/env python
"""Django's command-line utility for ServerSide performance testing server."""
import os
import sys


def main():
    """Run administrative tasks for ServerSide server."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ServerSide.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Print server info on runserver
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print("=" * 60)
        print("🚀 Starting ServerSide Performance Testing Server")
        print("=" * 60)
        print("Server: http://127.0.0.1:8001")
        print("WebSocket: ws://127.0.0.1:8001/ws/alerts/")
        print("Long Polling: http://127.0.0.1:8001/api/poll/alerts/")
        print("Push API: http://127.0.0.1:8001/api/push/")
        print("Health Check: http://127.0.0.1:8001/api/status/")
        print("=" * 60)

        # Add port if not specified
        if len(sys.argv) == 2:
            sys.argv.append('8001')

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
