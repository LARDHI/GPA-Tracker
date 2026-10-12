"""T0 smoke test: the package imports and pytest runs."""

import gpa_tracker


def test_package_imports():
    assert gpa_tracker.__doc__
