import time

# Connection module : We cab use it to test if database
# connection is available
from django.db import connections
# OperationalError : That django will throw when the database
# is isn't available
from django.db.utils import OperationalError
# BaseCommand : We use this to buld our custom command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Wating for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database Unavailable, waiting 1 second')
                time.sleep(1)
        # print with green color
        self.stdout.write(self.style.SUCCESS('Database available!'))
