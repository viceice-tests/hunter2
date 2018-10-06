#!/usr/bin/env python

# Copyright (C) 2018 The Hunter2 Contributors.
#
# This file is part of Hunter2.
#
# Hunter2 is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Hunter2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with Hunter2.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys

if __name__ == "__main__":
    # TODO: remove this when silk stops being bullshit
    if 'makemigrations' in sys.argv:  # nocover
        os.environ['H2_SILK'] = "False"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hunter2.settings")
    from django.core.management import execute_from_command_line

    # Probably more can be added here:
    if sys.argv[1] not in ['collectstatic', 'graph_models', 'help']:
        # Wait for a connection to the database to become available
        from hunter2.settings import DATABASES
        import wait
        print("Waiting for database connection...", file=sys.stderr)
        DB_HOST = DATABASES['default']['HOST']
        DB_PORT = DATABASES['default']['PORT']
        if not wait.tcp.open(DB_PORT, host=DB_HOST, timeout=10):  # nocover
            print("Failed to connect to database.", file=sys.stderr)
            sys.exit(1)

    # Launch the django command line
    execute_from_command_line(sys.argv)
