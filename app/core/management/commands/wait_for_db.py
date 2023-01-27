"""
Django command to wait for the database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default']) #if databases is not ready then throw an exception
                db_up = True # when self.check(databases = ['default'] returns true, 
                             # it won't throw exceptions and set db_up = True to stop while loop)
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second ..')
                time.sleep(1) # stop for 1s then retry

        self.stdout.write(self.style.SUCCESS('Database available!'))

