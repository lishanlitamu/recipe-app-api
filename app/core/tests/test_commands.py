"""
Test custom Django management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

#mock test
@patch('core.management.commands.wait_for_db.Command.check') #check the Command method from wait_for_db.py 
# this @patch points to patched_check see below
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database is ready."""
        patched_check.return_value = True
        call_command('wait_for_db')
        

        patched_check.assert_called_once_with(database=['default'])
    
    @patch('time.sleep') # points to patched_sleep
    #time.sleep returns none value whenever calling it, it's used to override the sleep so it won't actually sleep like it should while waiting for db getting ready
    # it will continue the execuation without sleeping in unit test
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        # Raise an exception instead of returning a value as used above with .return_value
        # The first two times of calling, we want to raise a Pyscopg2Error
        # switch to next line using \
        # The next three times raise OperationalError
        # [True] => input is True, a value => should return True, a value
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(database=['default'])







