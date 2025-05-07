from __future__ import annotations
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile
from typing import Self, TextIO

from .formatting import h_rule

class test_file_runner:
    def __init__(self, module_name: str):
        self.module_name = module_name


    def __get__(self, instance, owner):
        @differential(owner.correct_class, owner.student_class)
        def runner(grader_self, tested_class):
            obj = tested_class(*self.ctor_args, **self.ctor_kwargs)
            tested_method = getattr(obj, owner.method_name)
            return tested_method(*self.m_args, **self.m_kwargs)

        # we have to wrap the runner and pass the instance because our
        # returned function isn't bound as a method by default
        return lambda: runner(instance)


def run_test_file(test_file: Path | str):
    report_log = run_pytest_suite(test_file)

    if not report_log.success:
        print("======================== Issues while testing testFile.py ======================== \n\n")
        print("Failing tests:")
        for failing in report_log.failed_tests:
            print(f'    {failing}')

            print("It seems like one or more tests are failing.")
            print("Ensure that there are no failing tests in the testFile.py file.")
            print()

            print(f"Pytest output:")

            print(report_log.pretty)
            h_rule()


def run_pytest_suite(test_file: Path | str) -> TestReportLog:
    with NamedTemporaryFile as log_file:
        result = subprocess.run(['pytest', '--report-log={log_file.name}',
                                 str(test_file)],
                                capture_output=True, text=True)

        log_file.seek(0)
        return TestReportLog.from_run(result.stdout, log_file)

@dataclass
class TestingLog:
    success: bool  # whether the test suite was successful
    pretty: str  # the text returned to the console
    failed_tests: set[str]  # a list of failed tests
    raw_log: list[dict]  # the JSON log file

    __test__ = False  # make pytest ignore this because it's not a test class

    @classmethod
    def from_run(cls, captured_stdout: str, log_file: TextIO) -> Self:
        log = cls.read_json_log(log_file)

        success = cls.read_success(log)
        pretty = captured_stdout
        failed_tests = cls.read_failed_tests(log)

        return cls(success, pretty, failed_tests, log)

    @staticmethod
    def read_json_log(pytest_report_log: TextIO) -> list[dict]:
        data = []
        for line in pytest_report_log:
            data.append(json.loads(line))

        return data

    @staticmethod
    def read_success(log: list[dict]) -> bool:
        for line in log:
            try:
                return line['exitstatus'] == 0
            except KeyError:
                pass

        raise ValueError("Cannot find exitstatus in pytest log.")


    @staticmethod
    def read_failed_tests(log: TextIO) -> set[str]:
        failed = set()
        for line in log:
            try:
                node_id = line['nodeid']
                outcome = line['outcome']
            except KeyError:
                continue

            if not node_id:
                continue

            if outcome == 'failed':
                failed.add(node_id)

        return failed





#     def extract_failed_tests(self, pytest_output):
#         lines = pytest_output.split('\n')
#         failed_tests = []
#         capture = False
#
#         for line in lines:
#             if "short test summary info" in line:
#                 capture = True
#             elif line.startswith('============'):
#                 capture = False
#             elif capture:
#                 test_name = line.split()[1]
#                 failed_tests.append(test_name)
#
#         return failed_tests
#

#
#     def find_methods_with_lines(self, file_path, lines_of_interest):
#         with open(file_path, 'r') as file:
#             lines = file.readlines()
#
#         methods = set()
#         current_method = None
#         lines_found = 0
#
#         for i, line in enumerate(lines, start=1):
#             if line.strip().startswith("def "):
#                 current_method = line.strip().split('(')[0].replace("def ", "")
#             if i in lines_of_interest:
#                 if current_method not in methods:
#                     methods.add(current_method)
#                 lines_found += 1
#                 if lines_found == len(lines_of_interest):
#                     break
#
#         return methods
#
#     @partial_credit(test_cases_score)
#     def test_TestFile(self, set_score=None):
#         ''' Test testFile.py '''
#         import os, json
#         if "testFile.py" not in os.listdir("/autograder/submission/"):
#             self.fail("testFile.py is not submitted!!!")
#         else:
#             os.system("cp /autograder/submission/testFile.py /autograder/source/testFile.py")
#
#         total_score = 0
#
#         print("Note: This is an Automated test. There will be a penalty for any missing tests as part of the manual grading process.\n")
#
#         testfile_validation = self.check_pytest_suite("/autograder/source/testFile.py")
#         assert_failing_tests = []
#         if type(testfile_validation) == str:
#             assert_failing_tests = self.extract_failed_tests(testfile_validation)
#             # print(assert_failing_tests)
#             print("======================== Issues while testing testFile.py ======================== \n\n")
#             print(f"There is an error in testFile.py and the trace is as follows:\n" \
#                              f"{testfile_validation}\n"
#                      f"It seems like one or more tests are failing.\n"
#                      f"Do ensure that there are no failing tests in the testFile.py file.\n\n")
#             print(f"==================================================================================== \n\n")
#         failing_asserts_config = {}
#         for file in self.test_file_config:
#             failing_asserts_config[file] = []
#             for test in assert_failing_tests:
#                 if f"{file.split('.')[0]}::" in test:
#                     failing_asserts_config[file].append(test)
#                     assert_failing_tests.remove(test)
#
#         partially_correct = False
#
#         for file in self.test_file_config:
#             print(f"======================== Issues while testing {file} ======================== \n\n")
#             try:
#                 asserts_failing = False
#                 if len(failing_asserts_config[file]) > 0:
#                     asserts_failing = True
#                     print(f"Asserts failing for {file} as part of Test Methods: {', '.join(failing_asserts_config[file])}\n")
#                 elif len(assert_failing_tests)!=0 and f"{file.split('.')[0]}::" in testfile_validation:
#                     asserts_failing = True
#                     print(f"There seems to be an error with tests written for {file}. Refer to the error trace of testFile.py \n")
#
#                 coverage_command = f"python3 -m pytest /autograder/source/testFile.py --cov-report=json:coverage.json --cov-config=/autograder/source/tests/.coveragerc --cov={file.split('.')[0]} > /dev/null"
#                 os.system(coverage_command)
#                 with open('coverage.json') as coverage_info:
#                     coverage = json.load(coverage_info)['files']
#                     if coverage[file]['summary']['percent_covered'] < 100:
#                         partially_correct = True
#                         print(f"Missing some test cases for logic written in {file}\n")
#                         print(f"Lines of code not tested as part of {file}: {', '.join([str(line) for line in coverage[file]['missing_lines']])}\n")
#                         methods_not_tested = self.find_methods_with_lines(f"/autograder/source/{file}", coverage[file]['missing_lines'])
#                         print(f"Methods not tested fully as part of {file}: {', '.join(methods_not_tested)}\n")
#                         # total_score += score_per_class * (coverage[file]['summary']['percent_covered']/100)
#                     elif not asserts_failing:
#                         print(f"Congratulations! Your tests work for {file}\n")
#                         total_score += self.test_file_config[file]
#             except:
#                 print(f"No tests written for logic as part of {file}")
#             print(f"==================================================================================== \n\n")
#
#         if partially_correct:
#             print(f"Refer to the logic in the above mentioned lines/methods and add more test cases to cover them in testFile.py\n\n")
#
#         # set_score(int(total_score))
#         set_score(total_score)
