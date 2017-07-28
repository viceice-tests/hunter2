#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
import sys

if __name__ == "__main__":
    # TODO: remove this when silk stops being bullshit
    if 'makemigrations' in sys.argv:
        os.environ['H2_SILK'] = "False"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hunter2.settings")
    from django.core.management import execute_from_command_line

    # Wait for a connection to the database to become available
    from hunter2.settings import DATABASES
    import wait
    print("Waiting for database connection...")
    DB_HOST = DATABASES['default']['HOST']
    DB_PORT = DATABASES['default']['PORT']
    if not wait.tcp.open(DB_PORT, host=DB_HOST, timeout=10):
        print("Failed to connect to database.")
        sys.exit(1)

    # Launch the django command line
    execute_from_command_line(sys.argv)
