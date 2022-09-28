# Standard Library
import re

# Third Party
import pytest

# Our Libraries
from invoke_databricks_wheel_tasks.utils.databricks import (
    default_dbfs_artifact_path,
    default_dbfs_wheel_path,
    list_jobs,
)


def test_default_dbfs_artifact_path():
    # Given
    fake_branch_name = "fake_branch"

    # When
    result = default_dbfs_artifact_path(fake_branch_name)

    # Then
    assert result == f"dbfs:/FileStore/wheels/{fake_branch_name}/invoke-databricks-wheel-tasks/"


def test_default_dbfs_wheel_path():
    # Given
    fake_branch_name = "fake_branch"
    wheel_name = "invoke-databricks-wheel-tasks"
    target_pattern = (
        f"dbfs:/FileStore/wheels/{fake_branch_name}/{wheel_name}/{wheel_name.replace('-', '_')}-.*-py3-none-any\\.whl"
    )
    result_pattern = re.compile(target_pattern)

    # When
    result = default_dbfs_wheel_path(fake_branch_name)

    # Then
    assert result_pattern.match(result) is not None, f"Did not match {target_pattern} in {result}"


@pytest.mark.integration
def test_list_jobs(databricks_test_workspace):
    # Given

    # When
    result = list_jobs()

    # Then
    assert type(result) == dict
