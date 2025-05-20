from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TextIO

from .importing import path_to_module


RawTestingReport = list[dict]


RawCoverageReport = dict


@dataclass
class TestingReport:
    success: bool  # whether the test suite was successful
    pretty: str  # the text returned to the console
    failed_tests: set[str]  # a list of failed tests
    raw_report: list[dict]  # the JSON log file

    __test__ = False  # tell pytest to ignore this class during test discovery

    @classmethod
    def from_raw(cls, captured_stdout: str, raw_report: list[dict]) -> "TestingReport":
        success = cls.read_success(raw_report)
        pretty = captured_stdout
        failed_tests = cls.read_failed_tests(raw_report)

        return cls(success, pretty, failed_tests, raw_report)

    @staticmethod
    def read_success(log: list[dict]) -> bool:
        for line in log:
            try:
                return line['exitstatus'] == 0
            except KeyError:
                pass

        raise ValueError("Cannot find exitstatus in pytest log.")

    @staticmethod
    def read_failed_tests(log: list[dict]) -> set[str]:
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


@dataclass
class ModuleCoverage:
    imported: bool
    missing_lines: Optional[set[int]]

    @classmethod
    def from_json_obj(cls, obj: dict) -> "ModuleCoverage":
        missing_lines = set(obj['missing_lines'])
        return cls(imported=True, missing_lines=missing_lines)


@dataclass
class CoverageReport:
    modules: dict[str, ModuleCoverage]

    @classmethod
    def build_report(cls, cov_modules: Iterable[str],
                     pytest_cov_raw: dict | None,
                     search_path: Path | str) -> "CoverageReport":
        """Build a report, including files listed but not imported.
        search_path: root path of the modules."""

        cov_modules = set(cov_modules)
        included = set()

        modules = {}

        # sometimes, the coverage report may not generate at all
        # if no files are included.
        # in this scenario, pytest_cov_raw would be None.
        if pytest_cov_raw:
            files = pytest_cov_raw['files']
            for file_name, info in files.items():
                mod_name = path_to_module(file_name, search_path)
                included.add(mod_name)

                modules[mod_name] = ModuleCoverage.from_json_obj(info)

        not_included = cov_modules - included
        for mod in not_included:
            modules[mod] = ModuleCoverage(imported=False, missing_lines=None)

        return cls(modules)
