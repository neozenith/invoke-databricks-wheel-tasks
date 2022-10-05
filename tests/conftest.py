# Standard Library
import os
from pathlib import Path

# Third Party
import pytest
from dotenv import load_dotenv

load_dotenv("./tests/.env")


class FixtureConfigurationError(Exception):
    ...


@pytest.fixture(scope="function")
def databricks_test_workspace(monkeypatch):
    """Load environment variables for test databricks workspace fixture into monkeypatched environment variables.

    https://stackoverflow.com/a/70829371/622276

    If you are here because of a failing test suite then you need to either:
    A) Create a .env file which exports the below variables for your test databricks workspace
    B) Export the below environment variables into your CI system's secrets.
    """
    if (Path.home() / ".databrickscfg").exists():
        raise FixtureConfigurationError(
            "It looks like you have a ~/.databrickscfg. It is strongly advised to backup and remove this whilst testing to avoid polluting other workspaces unintentionally."
        )

    try:
        monkeypatch.setenv("DATABRICKS_HOST", os.environ["TEST_FIXTURE_DATABRICKS_HOST"])
        monkeypatch.setenv("DATABRICKS_TOKEN", os.environ["TEST_FIXTURE_DATABRICKS_TOKEN"])
        monkeypatch.setenv("DATABRICKS_JOBS_API_VERSION", os.environ["TEST_FIXTURE_DATABRICKS_JOBS_API_VERSION"])
    except KeyError as k:
        error_message = """
        If you are here because of a failing test suite then you need to either:
            A) Create a .env file which exports the below variables for your test databricks workspace
            B) Export the below environment variables into your CI system's secrets.

            TEST_FIXTURE_DATABRICKS_HOST=https://<organisation-id>.cloud.databricks.com
            TEST_FIXTURE_DATABRICKS_TOKEN=<Personal Access Token>
            TEST_FIXTURE_DATABRICKS_JOBS_API_VERSION="2.1"

            These are prefixed with TEST_FIXTURE_ to differentiate them from any other real CLI credentials you might be using.
        """
        raise FixtureConfigurationError(error_message) from k
