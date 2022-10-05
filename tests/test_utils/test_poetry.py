# Standard Library
import re

# Our Libraries
from invoke_databricks_wheel_tasks.utils.poetry import (
    poetry_project_name,
    poetry_project_version,
    poetry_wheelname,
)


def test_poetry_project_name():
    # Given
    # .. testing for errors thrown is underlying poetry API changes

    # When
    name = poetry_project_name()

    # Then
    assert name == "invoke-databricks-wheel-tasks"


def test_poetry_project_version():
    # Given
    # .. testing for errors thrown is underlying poetry API changes
    target_pattern = "\\d+\\.\\d+\\.\\d+[a-z]*\\d*"
    result_pattern = re.compile(target_pattern)

    # When
    version = poetry_project_version()

    # Then
    assert result_pattern.match(version) is not None, f"Did not match pattern: {target_pattern} in string: {version}"


def test_poetry_wheelname():
    # Given
    # .. testing for errors thrown is underlying poetry API changes
    target_pattern = f"{poetry_project_name().replace('-', '_')}-.*-py3-none-any\\.whl"
    result_pattern = re.compile(target_pattern)

    # When
    wheelname = poetry_wheelname()

    # Then
    assert (
        result_pattern.match(wheelname) is not None
    ), f"Did not match pattern: {target_pattern} in string: {wheelname}"
