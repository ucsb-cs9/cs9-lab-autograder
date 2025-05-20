from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile
from typing import Any, cast, Optional, TextIO

from .formatting import h_rule
from .importing import submission_path, module_to_path, path_to_module
from .testing_report import (CoverageReport, RawCoverageReport,
                             RawTestingReport,
                             TestingReport)


class t_coverage:
    """A class descriptor which generates a coverage test."""
    def __init__(self, module_name: str):
        self.module_name = module_name

    def __get__(self, instance, owner):
        def coverage_runner():
            cov = owner.cov_report.modules[self.module_name]
            instance.assertTrue(cov.imported)
            instance.assertFalse(cov.missing_lines)

        return coverage_runner


class t_module:
    def __init__(self, module_name: str):
        self.module_name = module_name

    def __get__(self, instance, owner):
        def test_runner():
            instance.assertTrue(owner.testing_report.success)

        return test_runner


def run_unit_tests_and_coverage(test_module: str,
                                cov_modules: Optional[Iterable[str]],
                                search_path: Path | str) -> \
                                        Tuple[TestingReport,
                                              Optional[CoverageReport]]:

    file_name = module_to_path(test_module, search_path)
    stdout, raw_report, raw_cov = run_pytest(file_name,
                                             cov_modules=cov_modules)

    testing_report = TestingReport.from_raw(stdout, raw_report)

    cov_report = CoverageReport.build_report(
            cov_modules, raw_cov, search_path)

    return testing_report, cov_report


def run_pytest(test_file: Path | str,
               cov_modules: Optional[Iterable[str]] = None)\
                       -> tuple[str, RawTestingReport,
                                Optional[RawCoverageReport]]:

    """Run pytest
    Note that the raw coverage report MAY still be none even if you have
    supplied modules to test

    returns captured stdout, raw log, and raw covrage report"""

    with NamedTemporaryFile(mode='w+', delete_on_close=False) as log_file:
        with NamedTemporaryFile(mode='w+', delete_on_close=False) as cov_report_file:

            args = ['pytest', f'--report-log={log_file.name}']

            if cov_modules:
                cov_mod_args = [f'--cov={m}' for m in cov_modules]
                args += cov_mod_args

                args.append(f'--cov-report=json:{cov_report_file.name}')

            args.append(str(test_file))

            result = subprocess.run(
                    args, capture_output=True, text=True,
                    cwd=submission_path())

            # the cast is just here to please mypy
            raw_report = parse_jsonl(cast(TextIO, log_file))

            raw_cov = None
            if cov_modules and not is_file_empty(cast(TextIO, cov_report_file)):
                raw_cov = json.load(cov_report_file)

            return result.stdout, raw_report, raw_cov


def parse_jsonl(f: TextIO) -> list:
    """Parse a jsonl file into a list of Python objects"""
    data = []
    for line in f:
        data.append(json.loads(line))

    return data


def is_file_empty(f: TextIO) -> bool:
    """Check if a file has a size of 0."""
    f.seek(0, os.SEEK_END)
    if not f.tell():
        return True
    f.seek(0)
    return False
