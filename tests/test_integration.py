# Standard Library
import json
import os
import shutil
from pathlib import Path
from typing import Tuple

# Third Party
import pytest
from invoke import Context

# Our Libraries
from invoke_databricks_wheel_tasks.tasks import run_job, upload
from invoke_databricks_wheel_tasks.utils.databricks import (
    create_or_reset_job,
    default_dbfs_artifact_path,
    list_jobs,
)
from invoke_databricks_wheel_tasks.utils.misc import load_config, merge_template


@pytest.fixture(scope="function")
def example_wheel() -> Tuple[Path, str]:
    """Build a minimal example wheel for simulating an integration test."""
    c = Context()
    source_path = Path("./tests/example_databricks_project/")
    dist_path = source_path / "dist"

    shutil.rmtree(dist_path, ignore_errors=True)
    c.run("which poetry", hide=False, echo=True)
    c.run(f"cd {str(source_path)} && poetry build -f wheel", hide=False, echo=True, pty=True, warn=False)

    wheel_name = [w for x in os.walk(source_path) for w in x[2] if w.endswith(".whl")][0]
    return (dist_path, wheel_name)


@pytest.fixture(scope="function")
def upload_target_path(databricks_test_workspace: None, example_wheel: Tuple[Path, str]):
    # Setup
    c = Context()
    target = default_dbfs_artifact_path()

    yield target

    # Teardown
    result = c.run(f"dbfs rm --recursive {target}", hide=True)
    assert result.stdout == "\rDelete finished successfully.\n"

    result = c.run(f"dbfs ls {target}", warn=True, hide=True)
    assert "RESOURCE_DOES_NOT_EXIST" in result.stdout


@pytest.fixture(scope="function")
def uploaded_wheel_path(databricks_test_workspace, example_wheel):
    # Setup
    c = Context()
    target = default_dbfs_artifact_path()
    source_path, wheel_name = example_wheel
    upload(c, source_path=source_path)

    yield (target, wheel_name)

    # Teardown
    result = c.run(f"dbfs rm --recursive {target}", hide=True)
    assert result.stdout == "\rDelete finished successfully.\n"

    result = c.run(f"dbfs ls {target}", warn=True, hide=True)
    assert "RESOURCE_DOES_NOT_EXIST" in result.stdout


@pytest.mark.integration
def test_upload(databricks_test_workspace: None, example_wheel: Path, upload_target_path: str):
    # Given
    c = Context()
    source_path, wheel_name = example_wheel

    # When
    upload(c, source_path=str(source_path))

    # Then
    result = c.run(f"dbfs ls {upload_target_path}", hide=True)
    assert len(result.stdout.splitlines()) == 1


@pytest.mark.integration
def test_create_job(databricks_test_workspace: None, uploaded_wheel_path: Tuple[Path, str]):
    # Given
    c = Context()
    dbfs_path, wheel_name = uploaded_wheel_path
    dbfs_wheel_path = str(Path(dbfs_path) / wheel_name)
    # TODO: parametrise job configuration scenarios like tests/test_utils/test_merge_template.py
    config_path = Path("./tests/example_databricks_project/jobs/config.yml")
    template_path = Path("./tests/example_databricks_project/jobs/template.json.j2")
    environment_variables = {
        "bronze_wheel": dbfs_wheel_path,
        "silver_wheel": dbfs_wheel_path,
        "gold_wheel": dbfs_wheel_path,
        "bronze_package": "projectname",
        "silver_package": "projectname",
        "gold_package": "projectname",
    }

    conf = load_config(str(config_path), environment_variables)
    job_json_string = merge_template(str(template_path), conf)
    job_definition = json.loads(job_json_string)
    existing_jobs = list_jobs()
    assert job_definition["name"] not in existing_jobs.keys()

    # When
    result = create_or_reset_job(job_definition)
    result_data = json.loads(result)
    job_id = result_data["job_id"]

    # Then
    updated_listing = list_jobs()

    assert existing_jobs != updated_listing
    assert job_id is not None

    # Awaits job to run and throws errors if it is borked.
    run_job(c, job_id)
    c.run(f"databricks jobs delete --job-id {job_id}", hide=True)
