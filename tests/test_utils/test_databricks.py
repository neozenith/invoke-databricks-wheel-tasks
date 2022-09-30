# Standard Library
import json
import re

# Third Party
import pytest
from invoke import Context

# Our Libraries
from invoke_databricks_wheel_tasks.utils.databricks import (
    default_dbfs_artifact_path,
    default_dbfs_wheel_path,
    list_jobs,
    wait_for_run_status,
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


@pytest.mark.integration
def test_wait_for_run_status(databricks_test_workspace, capsys):
    # Given
    c = Context()  # basic invoke Context with default config/
    job_id = "911628753476440"  # Simple example task already configured in workspace
    profile = None

    # When
    result = c.run(f"databricks jobs run-now --job-id {job_id}", hide=True)
    run_id = json.loads(result.stdout)["run_id"]
    wait_for_run_status(c, profile, run_id)

    # Then
    out, err = capsys.readouterr()
    assert err == ""
    assert len(out) > 0
