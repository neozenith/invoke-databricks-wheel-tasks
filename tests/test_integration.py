# Third Party
import pytest
from invoke import Context

# Our Libraries
from invoke_databricks_wheel_tasks.tasks import upload
from invoke_databricks_wheel_tasks.utils.databricks import default_dbfs_artifact_path


@pytest.fixture(scope="function")
def upload_target_path(databricks_test_workspace):
    # Setup
    c = Context()
    target = default_dbfs_artifact_path()
    # TODO: build the source example wheel automatically

    yield target

    # Teardown
    result = c.run(f"dbfs rm --recursive {target}", hide=True)
    assert result.stdout == "\rDelete finished successfully.\n"

    result = c.run(f"dbfs ls {target}", warn=True, hide=True)
    assert "RESOURCE_DOES_NOT_EXIST" in result.stdout


@pytest.mark.integration
def test_upload(databricks_test_workspace, upload_target_path):
    # Given
    c = Context()
    source_path = "./tests/example_databricks_project/dist/"

    # When
    upload(c, source_path=source_path)

    # Then
    result = c.run(f"dbfs ls {upload_target_path}", hide=True)
    assert len(result.stdout.splitlines()) == 1
