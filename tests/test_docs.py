"""The docs stay true. Pure Python, no app import: from the top folder run  python3 -m pytest tests/test_docs.py -q

Each test runs one check from scripts/check.py, so the script and the tests never disagree.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("check", ROOT / "scripts" / "check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


def test_links_and_anchors_work():
    problems = check.check_links()
    assert not problems, "\n".join(problems)


def test_no_long_dashes():
    problems = check.check_dashes()
    assert not problems, "\n".join(problems)


def test_no_three_dots():
    problems = check.check_three_dots()
    assert not problems, "\n".join(problems)


def test_every_guide_is_in_the_readme():
    if check.guides_table() is None:
        pytest.skip('README.md has no "All the guides" heading yet. Add it with one row per docs/*.md page.')
    problems = check.check_guides_table()
    assert not problems, "\n".join(problems)


def test_settings_match_the_code():
    problems = check.check_settings()
    assert not problems, "\n".join(problems)


def test_tools_match_the_code():
    assert check.mcp_tools(), "found no @mcp.tool in core/phygital_memory/server.py"
    problems = check.check_tools()
    assert not problems, "\n".join(problems)


def test_versions_match():
    problems = check.check_versions()
    assert not problems, "\n".join(problems)
