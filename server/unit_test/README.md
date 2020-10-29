## Unit test

The unit tests can be run with the command:
```
python -m unittest test_cases
```

It will take a few seconds to run the test cases, you will see the following message if all test cases pass:
```
.......
----------------------------------------------------------------------
Ran 8 tests in 1.967s

OK
```

If any test case failed, you will see the following message:
```
.....F..
======================================================================
FAIL: test_solver (test_cases.TestStringMethods)
Test case for testing the solver functions
----------------------------------------------------------------------
Traceback (most recent call last):
  File "~/planimation-backend/backend/server/unit_test/test_cases.py", line 327, in test_solver
    , msg="The generated object is different from the expected output")
AssertionError: False is not true : The generated object is different from the expected output

----------------------------------------------------------------------
Ran 8 tests in 3.279s

FAILED (failures=1)
```

If any exception being thrown in the test case, you will see the captical "E":
```
..E....
```
with the exception message.