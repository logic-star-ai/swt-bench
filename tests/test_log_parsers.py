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
    
    def test_parse_log_django_1(self):
        log = """\
Importing application ordering
Skipping setup of unused database(s): default, other.
System check identified no issues (0 silenced).
ERROR

======================================================================
ERROR: tests (unittest.loader._FailedTest)
----------------------------------------------------------------------
ImportError: Failed to import test module: tests
Traceback (most recent call last):
  File "/opt/miniconda3/envs/testbed/lib/python3.6/unittest/loader.py", line 153, in loadTestsFromName
    module = __import__(module_name)
  File "./tests/ordering/tests.py", line 3, in <module>
    from .models import MyModel  # Assuming MyModel is the model used for testing ordering
ImportError: cannot import name 'MyModel'


----------------------------------------------------------------------
Ran 1 test in 0.000s
"""
        res = parse_log_django(log)
        self.assertDictEqual(
            {
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

    def test_parse_log_django_3(self):
        log = """\
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
test_aggregate_subquery_annotation (expressions.tests.BasicExpressionsTests) ... ok
test_annotate_values_aggregate (expressions.tests.BasicExpressionsTests) ... ok
test_annotate_values_count (expressions.tests.BasicExpressionsTests) ... ok
test_annotate_values_filter (expressions.tests.BasicExpressionsTests) ... ok
test_annotation_with_outerref (expressions.tests.BasicExpressionsTests) ... ok
test_annotations_within_subquery (expressions.tests.BasicExpressionsTests) ... ok
test_arithmetic (expressions.tests.BasicExpressionsTests) ... ok
test_exist_single_field_output_field (expressions.tests.BasicExpressionsTests) ... ok
test_explicit_output_field (expressions.tests.BasicExpressionsTests) ... ok
test_filter_inter_attribute (expressions.tests.BasicExpressionsTests) ... ok
test_filter_with_join (expressions.tests.BasicExpressionsTests) ... ok
test_filtering_on_annotate_that_uses_q (expressions.tests.BasicExpressionsTests) ... ok
test_in_subquery (expressions.tests.BasicExpressionsTests) ... ok
test_incorrect_field_in_F_expression (expressions.tests.BasicExpressionsTests) ... ok
test_incorrect_joined_field_in_F_expression (expressions.tests.BasicExpressionsTests) ... ok
test_nested_subquery (expressions.tests.BasicExpressionsTests) ... ok
test_nested_subquery_outer_ref_2 (expressions.tests.BasicExpressionsTests) ... ok
test_nested_subquery_outer_ref_with_autofield (expressions.tests.BasicExpressionsTests) ... ok
test_new_object_create (expressions.tests.BasicExpressionsTests) ... ok
test_new_object_save (expressions.tests.BasicExpressionsTests) ... ok
test_object_create_with_aggregate (expressions.tests.BasicExpressionsTests) ... ok
test_object_update (expressions.tests.BasicExpressionsTests) ... ok
test_object_update_fk (expressions.tests.BasicExpressionsTests) ... ok
test_object_update_unsaved_objects (expressions.tests.BasicExpressionsTests) ... ok
test_order_by_exists (expressions.tests.BasicExpressionsTests) ... ok
test_order_by_multiline_sql (expressions.tests.BasicExpressionsTests) ... test_order_of_operations (expressions.tests.BasicExpressionsTests) ... ok
test_outerref (expressions.tests.BasicExpressionsTests) ... ok
test_outerref_mixed_case_table_name (expressions.tests.BasicExpressionsTests) ... ok
test_outerref_with_operator (expressions.tests.BasicExpressionsTests) ... ok
test_parenthesis_priority (expressions.tests.BasicExpressionsTests) ... ok
test_pickle_expression (expressions.tests.BasicExpressionsTests) ... ok
test_subquery (expressions.tests.BasicExpressionsTests) ... ok
test_subquery_filter_by_aggregate (expressions.tests.BasicExpressionsTests) ... ok
test_subquery_references_joined_table_twice (expressions.tests.BasicExpressionsTests) ... ok
test_ticket_11722_iexact_lookup (expressions.tests.BasicExpressionsTests) ... ok
test_ticket_16731_startswith_lookup (expressions.tests.BasicExpressionsTests) ... ok
test_ticket_18375_chained_filters (expressions.tests.BasicExpressionsTests) ... ok
test_ticket_18375_join_reuse (expressions.tests.BasicExpressionsTests) ... ok
test_ticket_18375_kwarg_ordering (expressions.tests.BasicExpressionsTests) ... ok
test_ticket_18375_kwarg_ordering_2 (expressions.tests.BasicExpressionsTests) ... ok
test_update (expressions.tests.BasicExpressionsTests) ... ok
test_update_inherited_field_value (expressions.tests.BasicExpressionsTests) ... ok
test_update_with_fk (expressions.tests.BasicExpressionsTests) ... ok
test_update_with_none (expressions.tests.BasicExpressionsTests) ... ok
test_uuid_pk_subquery (expressions.tests.BasicExpressionsTests) ... ok
test_lefthand_addition (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_bitwise_and (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_bitwise_left_shift_operator (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_bitwise_or (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_bitwise_right_shift_operator (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_division (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_modulo (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_multiplication (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_power (expressions.tests.ExpressionOperatorTests) ... ok
test_lefthand_subtraction (expressions.tests.ExpressionOperatorTests) ... ok
test_right_hand_addition (expressions.tests.ExpressionOperatorTests) ... ok
test_right_hand_division (expressions.tests.ExpressionOperatorTests) ... ok
test_right_hand_modulo (expressions.tests.ExpressionOperatorTests) ... ok
test_right_hand_multiplication (expressions.tests.ExpressionOperatorTests) ... ok
test_right_hand_subtraction (expressions.tests.ExpressionOperatorTests) ... ok
test_righthand_power (expressions.tests.ExpressionOperatorTests) ... ok
test_complex_expressions (expressions.tests.ExpressionsNumericTests) ... ok
test_fill_with_value_from_same_object (expressions.tests.ExpressionsNumericTests) ... ok
test_filter_not_equals_other_field (expressions.tests.ExpressionsNumericTests) ... ok
test_increment_value (expressions.tests.ExpressionsNumericTests) ... ok
test_F_reuse (expressions.tests.ExpressionsTests) ... ok
test_insensitive_patterns_escape (expressions.tests.ExpressionsTests) ... ok
test_patterns_escape (expressions.tests.ExpressionsTests) ... ok
test_date_comparison (expressions.tests.FTimeDeltaTests) ... ok
test_date_minus_duration (expressions.tests.FTimeDeltaTests) ... ok
test_date_subtraction (expressions.tests.FTimeDeltaTests) ... ok
test_datetime_subtraction (expressions.tests.FTimeDeltaTests) ... ok
test_datetime_subtraction_microseconds (expressions.tests.FTimeDeltaTests) ... ok
test_delta_add (expressions.tests.FTimeDeltaTests) ... ok
test_delta_subtract (expressions.tests.FTimeDeltaTests) ... ok
test_delta_update (expressions.tests.FTimeDeltaTests) ... ok
test_duration_with_datetime (expressions.tests.FTimeDeltaTests) ... ok
test_duration_with_datetime_microseconds (expressions.tests.FTimeDeltaTests) ... ok
test_durationfield_add (expressions.tests.FTimeDeltaTests) ... ok
test_exclude (expressions.tests.FTimeDeltaTests) ... ok
test_invalid_operator (expressions.tests.FTimeDeltaTests) ... ok
test_mixed_comparisons1 (expressions.tests.FTimeDeltaTests) ... skipped "Database doesn't support feature(s): supports_mixed_date_datetime_comparisons"
test_mixed_comparisons2 (expressions.tests.FTimeDeltaTests) ... ok
test_multiple_query_compilation (expressions.tests.FTimeDeltaTests) ... ok
test_negative_timedelta_update (expressions.tests.FTimeDeltaTests) ... ok
test_query_clone (expressions.tests.FTimeDeltaTests) ... ok
test_time_subtraction (expressions.tests.FTimeDeltaTests) ... ok
test_month_aggregation (expressions.tests.FieldTransformTests) ... ok
test_multiple_transforms_in_values (expressions.tests.FieldTransformTests) ... ok
test_transform_in_values (expressions.tests.FieldTransformTests) ... ok
test_complex_expressions_do_not_introduce_sql_injection_via_untrusted_string_inclusion (expressions.tests.IterableLookupInnerExpressionsTests) ... ok
test_expressions_in_lookups_join_choice (expressions.tests.IterableLookupInnerExpressionsTests) ... ok
test_in_lookup_allows_F_expressions_and_expressions_for_datetimes (expressions.tests.IterableLookupInnerExpressionsTests) ... ok
test_in_lookup_allows_F_expressions_and_expressions_for_integers (expressions.tests.IterableLookupInnerExpressionsTests) ... ok
test_range_lookup_allows_F_expressions_and_expressions_for_integers (expressions.tests.IterableLookupInnerExpressionsTests) ... ok
test_deconstruct (expressions.tests.ValueTests) ... ok
test_deconstruct_output_field (expressions.tests.ValueTests) ... ok
test_equal (expressions.tests.ValueTests) ... ok
test_equal_output_field (expressions.tests.ValueTests) ... ok
test_hash (expressions.tests.ValueTests) ... ok
test_raise_empty_expressionlist (expressions.tests.ValueTests) ... ok
test_update_TimeField_using_Value (expressions.tests.ValueTests) ... ok
test_update_UUIDField_using_Value (expressions.tests.ValueTests) ... ok
test_and (expressions.tests.CombinableTests) ... ok
test_negation (expressions.tests.CombinableTests) ... ok
test_or (expressions.tests.CombinableTests) ... ok
test_reversed_and (expressions.tests.CombinableTests) ... ok
test_reversed_or (expressions.tests.CombinableTests) ... ok
test_deconstruct (expressions.tests.FTests) ... ok
test_deepcopy (expressions.tests.FTests) ... ok
test_equal (expressions.tests.FTests) ... ok
test_hash (expressions.tests.FTests) ... ok
test_not_equal_Value (expressions.tests.FTests) ... ok
test_aggregates (expressions.tests.ReprTests) ... ok
test_distinct_aggregates (expressions.tests.ReprTests) ... ok
test_expressions (expressions.tests.ReprTests) ... ok
test_filtered_aggregates (expressions.tests.ReprTests) ... ok
test_functions (expressions.tests.ReprTests) ... ok
test_equal (expressions.tests.SimpleExpressionTests) ... ok
test_hash (expressions.tests.SimpleExpressionTests) ... Testing against Django installed in '/testbed/django'
Importing application expressions
Skipping setup of unused database(s): other.
Operations to perform:
  Synchronize unmigrated apps: auth, contenttypes, expressions, messages, sessions, staticfiles
  Apply all migrations: admin, sites
Synchronizing apps without migrations:
  Creating tables...
    Creating table django_content_type
    Creating table auth_permission
    Creating table auth_group
    Creating table auth_user
    Creating table django_session
    Creating table expressions_employee
    Creating table expressions_remoteemployee
    Creating table expressions_company
    Creating table expressions_number
    Creating table expressions_ExPeRiMeNt
    Creating table expressions_result
    Creating table expressions_time
    Creating table expressions_simulationrun
    Creating table expressions_uuidpk
    Creating table expressions_uuid
    Running deferred SQL...
Running migrations:
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying sites.0001_initial... OK
  Applying sites.0002_alter_domain_unique... OK
System check identified no issues (0 silenced).
ok

======================================================================
ERROR: test_order_by_multiline_sql (expressions.tests.BasicExpressionsTests) (qs=<QuerySet []>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/testbed/django/db/backends/utils.py", line 85, in _execute
    return self.cursor.execute(sql, params)
  File "/testbed/django/db/backends/sqlite3/base.py", line 391, in execute
    return Database.Cursor.execute(self, query, params)
sqlite3.OperationalError: near ")": syntax error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "./tests/expressions/tests.py", line 407, in test_order_by_multiline_sql
    [self.example_inc, self.gmbh, self.foobar_ltd],
  File "/opt/miniconda3/envs/testbed/lib/python3.6/unittest/case.py", line 940, in assertSequenceEqual
    len1 = len(seq1)
  File "/testbed/django/db/models/query.py", line 255, in __len__
    self._fetch_all()
  File "/testbed/django/db/models/query.py", line 1231, in _fetch_all
    self._result_cache = list(self._iterable_class(self))
  File "/testbed/django/db/models/query.py", line 54, in __iter__
    results = compiler.execute_sql(chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
  File "/testbed/django/db/models/sql/compiler.py", line 1080, in execute_sql
    cursor.execute(sql, params)
  File "/testbed/django/db/backends/utils.py", line 68, in execute
    return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
  File "/testbed/django/db/backends/utils.py", line 77, in _execute_with_wrappers
    return executor(sql, params, many, context)
  File "/testbed/django/db/backends/utils.py", line 85, in _execute
    return self.cursor.execute(sql, params)
  File "/testbed/django/db/utils.py", line 89, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/testbed/django/db/backends/utils.py", line 85, in _execute
    return self.cursor.execute(sql, params)
  File "/testbed/django/db/backends/sqlite3/base.py", line 391, in execute
    return Database.Cursor.execute(self, query, params)
django.db.utils.OperationalError: near ")": syntax error

======================================================================
FAIL: test_order_by_multiline_sql (expressions.tests.BasicExpressionsTests) (qs=<QuerySet []>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "./tests/expressions/tests.py", line 407, in test_order_by_multiline_sql
    [self.example_inc, self.gmbh, self.foobar_ltd],
AssertionError: Sequences differ: <QuerySet [<Company: Example Inc.>, <Comp[36 chars]bH>]> != [<Company: Example Inc.>, <Company: Test [25 chars]td.>]

First differing element 1:
<Company: Foobar Ltd.>
<Company: Test GmbH>

- <QuerySet [<Company: Example Inc.>, <Company: Foobar Ltd.>, <Company: Test GmbH>]>
+ [<Company: Example Inc.>, <Company: Test GmbH>, <Company: Foobar Ltd.>]

----------------------------------------------------------------------
Ran 121 tests in 4.205s

FAILED (failures=1, errors=1, skipped=1)
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
"""
        res = parse_log_django(log)
        ks = [k for k in res.keys() if "test_order_by_multiline_sql" in k]
        print(ks)
        self.assertEqual(1, len(ks))

    def test_django_log_parser_4(self):
        log = """\
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
test_migrate_test_setting_false (backends.base.test_creation.TestDbCreationTests) ... ok
test_migrate_test_setting_true (backends.base.test_creation.TestDbCreationTests) ... ok
test_custom_test_name (backends.base.test_creation.TestDbSignatureTests) ... ok
test_custom_test_name_with_test_prefix (backends.base.test_creation.TestDbSignatureTests) ... ok
test_default_name (backends.base.test_creation.TestDbSignatureTests) ... ok
test_circular_reference (backends.base.test_creation.TestDeserializeDbFromString) ... ok
test_circular_reference_with_natural_key (backends.base.test_creation.TestDeserializeDbFromString) ... ok
test_self_reference (backends.base.test_creation.TestDeserializeDbFromString) ... ok
app_unmigrated (unittest.loader._FailedTest) ... ERROR

======================================================================
ERROR: app_unmigrated (unittest.loader._FailedTest)
----------------------------------------------------------------------
ImportError: Failed to import test module: app_unmigrated
Traceback (most recent call last):
  File "/opt/miniconda3/envs/testbed/lib/python3.6/unittest/loader.py", line 153, in loadTestsFromName
    module = __import__(module_name)
ModuleNotFoundError: No module named 'backends.base.app_unmigrated'


----------------------------------------------------------------------
Ran 9 tests in 0.800s

FAILED (errors=1)
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Testing against Django installed in '/testbed/django'
Importing application backends
Skipping setup of unused database(s): other.
Operations to perform:
  Synchronize unmigrated apps: auth, backends, contenttypes, messages, sessions, staticfiles
  Apply all migrations: admin, sites
Synchronizing apps without migrations:
  Creating tables...
    Creating table django_content_type
    Creating table auth_permission
    Creating table auth_group
    Creating table auth_user
    Creating table django_session
    Creating table backends_square
    Creating table backends_person
    Creating table backends_schoolclass
    Creating table backends_verylongmodelnamezzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
    Creating table backends_tag
    Creating table CaseSensitive_Post
    Creating table backends_reporter
    Creating table backends_article
    Creating table backends_item
    Creating table backends_object
    Creating table backends_objectreference
    Creating table backends_objectselfreference
    Creating table backends_circulara
    Creating table backends_circularb
    Creating table backends_rawdata
    Creating table backends_author
    Creating table backends_book
    Running deferred SQL...
Running migrations:
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying sites.0001_initial... OK
  Applying sites.0002_alter_domain_unique... OK
System check identified no issues (0 silenced).
"""
        parse_log_django(log)
    
    def test_django_log_parser_5(self):
        log = """\
test_watched_roots_contains_files (utils_tests.test_autoreload.WatchmanReloaderTests) ... skipped 'Watchman unavailable: Cannot connect to the watchman service.'
test_watched_roots_contains_sys_path (utils_tests.test_autoreload.WatchmanReloaderTests) ... skipped 'Watchman unavailable: Cannot connect to the watchman service.'

----------------------------------------------------------------------
Ran 73 tests in 1.045s

OK (skipped=21)
"""
        res = parse_log_django(log)
        self.assertDictEqual(
            {
                "test_watched_roots_contains_files (utils_tests.test_autoreload.WatchmanReloaderTests)": "SKIPPED",
                "test_watched_roots_contains_sys_path (utils_tests.test_autoreload.WatchmanReloaderTests)": "SKIPPED",
            },
            res,
        )

    def test_django_log_parser_6(self):
        log = """\
test_get_FIELD_display_translated (model_fields.tests.GetFieldDisplayTests)
A translated display value is coerced to str. ... ok
test_iterator_choices (model_fields.tests.GetFieldDisplayTests) ... ok
test_overriding_FIELD_display (model_fields.tests.GetFieldDisplayTests) ... Testing against Django installed in '/testbed/django'
Importing application model_fields
Skipping setup of unused database(s): other.
Operations to perform:
  Synchronize unmigrated apps: auth, contenttypes, messages, model_fields, sessions, staticfiles
  Apply all migrations: admin, sites
Synchronizing apps without migrations:
  Creating tables...
    Creating table django_content_type
    Creating table auth_permission
    Creating table auth_group
    Creating table auth_user
    Creating table django_session
    Creating table model_fields_foo
    Creating table model_fields_bar
    Creating table model_fields_whiz
    Creating table model_fields_whizdelayed
    Creating table model_fields_whiziter
    Creating table model_fields_whiziterempty
    Creating table model_fields_choiceful
    Creating table model_fields_bigd
    Creating table model_fields_floatmodel
    Creating table model_fields_bigs
    Creating table model_fields_unicodeslugfield
    Creating table model_fields_automodel
    Creating table model_fields_bigautomodel

    Creating table model_fields_personwithheightandwidth
    Creating table model_fields_persondimensionsfirst
    Creating table model_fields_persontwoimages
    Creating table model_fields_allfieldsmodel
    Creating table model_fields_manytomany
    Creating table model_fields_uuidmodel
    Creating table model_fields_nullableuuidmodel
    Creating table model_fields_primarykeyuuidmodel
    Creating table model_fields_relatedtouuidmodel
    Creating table model_fields_uuidchild
    Creating table model_fields_uuidgrandchild
    Running deferred SQL...
Running migrations:
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying sites.0001_initial... OK
  Applying sites.0002_alter_domain_unique... OK
System check identified no issues (0 silenced).
FAIL

======================================================================
FAIL: test_overriding_FIELD_display (model_fields.tests.GetFieldDisplayTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "./tests/model_fields/tests.py", line 179, in test_overriding_FIELD_display
    self.assertEqual(f.get_foo_bar_display(), 'something')
AssertionError: 'foo' != 'something'
- foo
+ something


----------------------------------------------------------------------
Ran 31 tests in 0.180s
"""
        res = parse_log_django(log)
        self.assertDictEqual(
            {
                "test_overriding_FIELD_display (model_fields.tests.GetFieldDisplayTests)": "FAILED",
                "test_get_FIELD_display_translated (model_fields.tests.GetFieldDisplayTests)": "PASSED",
                "test_iterator_choices (model_fields.tests.GetFieldDisplayTests)": "PASSED",
            },
            res,
        )

    def test_django_log_parser_7(self):
        log = """\
test_default_name (backends.base.test_creation.TestDbSignatureTests) ... ok
test_circular_reference (backends.base.test_creation.TestDeserializeDbFromString) ... Testing against Django installed in '/testbed/django'
Importing application backends
Skipping setup of unused database(s): other.
Operations to perform:
  Synchronize unmigrated apps: auth, backends, contenttypes, messages, sessions, staticfiles
  Apply all migrations: admin, sites
Synchronizing apps without migrations:
  Creating tables...
    Creating table django_content_type
    Creating table auth_permission
    Creating table auth_group
    Creating table auth_user
    Creating table django_session
    Creating table backends_square
    Creating table backends_person
    Creating table backends_schoolclass
    Creating table backends_verylongmodelnamezzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
    Creating table backends_tag
    Creating table CaseSensitive_Post
    Creating table backends_reporter
    Creating table backends_article
    Creating table backends_item
    Creating table backends_object
    Creating table backends_objectreference
    Creating table backends_rawdata
    Creating table backends_author
    Creating table backends_book
    Running deferred SQL...
Running migrations:
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying sites.0001_initial... OK
  Applying sites.0002_alter_domain_unique... OK
System check identified no issues (0 silenced).
ok

----------------------------------------------------------------------
Ran 6 tests in 0.107s

OK
"""
        res = parse_log_django(log)
        self.assertDictEqual(
            {
                "test_default_name (backends.base.test_creation.TestDbSignatureTests)": "PASSED",
                "test_circular_reference (backends.base.test_creation.TestDeserializeDbFromString)": "PASSED",
            },
            res,
        )

class ParseSympyLogTest(unittest.TestCase):
    def test_parse_sympy_log(self):
        log = """\
/testbed/sympy/core/basic.py:3: DeprecationWarning: Using or importing the ABCs from 'collections' instead of from 'collections.abc' is deprecated since Python 3.3, and in 3.10 it will stop working
  from collections import Mapping
/testbed/sympy/plotting/plot.py:28: DeprecationWarning: Using or importing the ABCs from 'collections' instead of from 'collections.abc' is deprecated since Python 3.3, and in 3.10 it will stop working
  from collections import Callable
============================= test process starts ==============================
executable:         /opt/miniconda3/envs/testbed/bin/python3  (3.9.19-final-0) [CPython]
architecture:       64-bit
cache:              no
ground types:       python 
random seed:        87151617
hash randomization: on (PYTHONHASHSEED=3328767817)

sympy/printing/tests/test_ccode.py[32] 
test_printmethod ok
test_ccode_sqrt ok
test_ccode_Pow ok
test_ccode_constants_mathh ok
test_ccode_constants_other ok
test_ccode_Rational ok
test_ccode_Integer ok
test_ccode_functions ok
test_ccode_inline_function ok
test_ccode_exceptions ok
test_ccode_user_functions ok
test_ccode_boolean ok
test_ccode_Relational F
test_ccode_Piecewise ok
test_ccode_sinc F
test_ccode_Piecewise_deep ok
test_ccode_ITE ok
test_ccode_settings ok
test_ccode_Indexed ok
test_ccode_Indexed_without_looking_for_contraction ok
test_ccode_loops_matrix_vector ok
test_dummy_loops ok
test_ccode_loops_add ok
test_ccode_loops_multiple_contractions ok
test_ccode_loops_addfactor ok
test_ccode_loops_multiple_terms ok
test_dereference_printing ok
test_Matrix_printing ok
test_ccode_reserved_words ok
test_ccode_sign ok
test_ccode_Assignment ok
test_ccode_For ok                                                         [FAIL]


________________________________________________________________________________
___________ sympy/printing/tests/test_ccode.py:test_ccode_Relational ___________
  File "/testbed/sympy/printing/tests/test_ccode.py", line 125, in test_ccode_Relational
    assert ccode(Eq(x, y)) == "x == y"
AssertionError
________________________________________________________________________________
______________ sympy/printing/tests/test_ccode.py:test_ccode_sinc ______________
  File "/testbed/sympy/printing/tests/test_ccode.py", line 178, in test_ccode_sinc
    assert ccode(expr) == (
AssertionError

============= tests finished: 30 passed, 2 failed, in 0.46 seconds =============
DO *NOT* COMMIT!
    """
        res = parse_log_sympy(log)
        self.assertEqual(res.get("test_ccode_Relational"), "FAILED")
        self.assertEqual(res.get("test_ccode_sinc"), "FAILED")
        self.assertEqual(res.get("test_ccode_For"), "PASSED")
        self.assertEqual(res.get("sympy/printing/tests/test_ccode"), None)
        
    def test_parse_sympy_log_1(self):
        log = """\
============================= test process starts ==============================
executable:         /opt/miniconda3/envs/testbed/bin/python3  (3.9.19-final-0) [CPython]
architecture:       64-bit
cache:              no
ground types:       python 
numpy:              None
random seed:        9713485
hash randomization: on (PYTHONHASHSEED=4179724166)

sympy/physics/units/tests/test_prefixes.py[4] 
test_prefix_operations F
test_prefix_unit ok
test_bases ok
test_repr ok                                                              [FAIL]


________________________________________________________________________________
______ sympy/physics/units/tests/test_prefixes.py::test_prefix_operations ______
Traceback (most recent call last):
  File "/testbed/sympy/physics/units/tests/test_prefixes.py", line 20, in test_prefix_operations
    assert m * k is S.One
AssertionError

============= tests finished: 3 passed, 1 failed, in 0.94 seconds ==============
DO *NOT* COMMIT!
    """
        res = parse_log_sympy(log)
        self.assertDictEqual(
            {
                "test_prefix_operations": "FAILED",
                "test_repr": "PASSED",
                "test_bases": "PASSED",
                "test_prefix_unit": "PASSED",
            },
            res,
        )