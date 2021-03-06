#!/usr/bin/env python

import sys

import django

from django.conf import settings

from nose import run_exit


if not settings.configured:
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "django-inspect.db",
            }
        },
        INSTALLED_APPS=[
            "tests.test_app",
        ]
    )

try:
    django.setup()
except AttributeError:
    pass

if __name__ == "__main__":
    run_exit(argv=sys.argv)
