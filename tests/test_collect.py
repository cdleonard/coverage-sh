"""
Test collection of coverage data

This is meant to allow testing just the bash hooking behavior without passing
through the tree-sitter parsing and reporting logic.
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest
from coverage import CoverageData

from coverage_sh.plugin import CoverageParserThread, CoverageWriter, init_helper
from tests.test_plugin import SYNTAX_EXAMPLE_COVERED_LINES, SYNTAX_EXAMPLE_STDOUT


@dataclass
class RunCollectResult:
    proc: subprocess.CompletedProcess[str]
    cov_data: CoverageData
    lines: set[int]


def run_shell_collect(script_path: Path, tmp_path: Path) -> RunCollectResult:
    """Run a shell script and collect coverage data, without reporting"""
    if os.environ.get("COV_CORE_DATAFILE"):
        pytest.skip("Can't run with COV_CORE_DATAFILE set")  # pragma: no cover
    coverage_data_path = tmp_path.joinpath(".coverage")
    parser_thread = CoverageParserThread(
        coverage_writer=CoverageWriter(coverage_data_path),
        name=f"CoverageParserThread({coverage_data_path!s})",
    )
    parser_thread.start()
    helper_path = init_helper(parser_thread.fifo_path)
    xenv = os.environ.copy()
    xenv["BASH_ENV"] = str(helper_path)
    xenv["ENV"] = str(helper_path)
    proc = subprocess.run(
        str(script_path),
        env=xenv,
        check=False,
        text=True,
        capture_output=True,
    )
    parser_thread.stop()
    parser_thread.join(timeout=5)
    assert not parser_thread.is_alive()
    cov_files = list(Path(tmp_path).glob(".coverage*"))
    assert len(cov_files) == 1
    cov_data = CoverageData(basename=str(cov_files[0]), suffix="")
    cov_data.read()
    assert cov_data.measured_files() == {str(script_path)}
    assert cov_data.data_filename() == str(cov_files[0])
    cov_lines = cov_data.lines(str(script_path))
    assert cov_lines is not None
    return RunCollectResult(
        proc=proc,
        cov_data=cov_data,
        lines=set(cov_lines),
    )


def test_syntax_example(resources_dir: Path, tmp_path: Path) -> None:
    script_path = resources_dir / "syntax_example.sh"
    result = run_shell_collect(script_path, tmp_path)
    assert result.proc.stdout == SYNTAX_EXAMPLE_STDOUT
    assert result.proc.returncode == 0
    assert result.lines == set(SYNTAX_EXAMPLE_COVERED_LINES)


def test_multi_line(resources_dir: Path, tmp_path: Path) -> None:
    script_path = resources_dir.joinpath("test_multi_line.sh")
    out_text = resources_dir.joinpath("test_multi_line.out").read_text()
    result = run_shell_collect(script_path, tmp_path)
    assert result.proc.stdout == out_text
    assert result.proc.returncode == 0
    assert result.lines == {3, 4, 7, 10}
