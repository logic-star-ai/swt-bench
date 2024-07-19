import unittest
from src.log_parsers import *

class TestDjangoLogParser(unittest.TestCase):

    def test_parse_log_django(self):
        log = """\
test_callable_path (model_fields.test_filepathfield.FilePathFieldTests) ... ERROR
test_path (model_fields.test_filepathfield.FilePathFieldTests) ... Testing against Django installed in '/testbed/django'
Importing application model_fields
Skipping setup of unused database(s): default, other.
System check identified no issues (0 silenced).
ok

======================================================================
ERROR: test_callable_path (model_fields.test_filepathfield.FilePathFieldTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "./tests/model_fields/test_filepathfield.py", line 22, in test_callable_path
    self.assertEqual(field.formfield().path, path)
  File "/testbed/django/db/models/fields/__init__.py", line 1718, in formfield
    **kwargs,
  File "/testbed/django/db/models/fields/__init__.py", line 890, in formfield
    return form_class(**defaults)
  File "/testbed/django/forms/fields.py", line 1109, in __init__
    for f in os.scandir(self.path):
TypeError: scandir: path should be string, bytes, os.PathLike or None, not function

----------------------------------------------------------------------
Ran 2 tests in 0.006s

FAILED (errors=1)
    """
        res = parse_log_django(log)
        self.assertDictEqual(
            {
                "test_callable_path (model_fields.test_filepathfield.FilePathFieldTests)": "ERROR",
                "test_path (model_fields.test_filepathfield.FilePathFieldTests)": "PASSED",
            },
            res,
        )
    
    def test_parse_log_django_2(self):
        log = """\
test_callable_path (model_fields.test_filepathfield.FilePathFieldTests) ... ok
test_path (model_fields.test_filepathfield.FilePathFieldTests) ... Testing against Django installed in '/testbed/django'
Importing application model_fields
Skipping setup of unused database(s): default, other.
System check identified no issues (0 silenced).
ok

----------------------------------------------------------------------
Ran 2 tests in 0.004s

OK
"""
        res = parse_log_django(log)
        self.assertDictEqual(
            {
                "test_callable_path (model_fields.test_filepathfield.FilePathFieldTests)": "PASSED",
                "test_path (model_fields.test_filepathfield.FilePathFieldTests)": "PASSED",
            },
            res,
        )
