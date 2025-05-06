import unittest

class TestTester():
    def assertTestCaseNoFailure(self, test_case_class):
        """Run a TestCase and assert that it has no errors or failures."""
        self.assertTestCaseFailure(test_case_class, failures=0)


    def assertTestCaseFailure(self, test_case_class, failures=1):
        """Run a TestCase and assert that it has a particular amount of
        failures."""
        loader = unittest.TestLoader()
        test_suite = loader.loadTestsFromTestCase(test_case_class)

        result = unittest.TestResult()
        test_suite.run(result)

        error_msg = '\n'.join(x[1] for x in result.errors)
        self.assertEqual(0, len(result.errors), msg=error_msg)

        failure_msg = '\n'.join(x[1] for x in result.failures)
        self.assertEqual(failures, len(result.failures), msg=failure_msg)
