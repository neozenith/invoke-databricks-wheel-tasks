# Standard Library
import json
import os
import time
from functools import lru_cache
from pprint import pprint as pp
from typing import Any, Dict, List, Optional

# Third Party
import invoke

from .git import git_current_branch
from .poetry import poetry_project_name, poetry_wheelname

POLL_DELAY = 5


@lru_cache(maxsize=None)
def default_dbfs_artifact_path(branch_name: Optional[str] = None) -> str:
    """Helper to construct a default artifact path to upload to in DBFS."""
    if branch_name is None:
        branch_name = git_current_branch()
    return f"dbfs:/FileStore/wheels/{branch_name}/{poetry_project_name()}/"


@lru_cache(maxsize=None)
def default_dbfs_wheel_path(branch_name: Optional[str] = None) -> str:
    """Helper to construct a default artifact path to upload to in DBFS."""
    return f"{default_dbfs_artifact_path(branch_name)}{poetry_wheelname()}"


def list_jobs(profile: Optional[str] = None) -> Dict[str, str]:
    """List Jobs from databricks workspace.

    Returns a dictionary with job names as keys and job IDs as values.
    """
    profile_flag = f"--profile {profile}" if profile else ""
    result = invoke.run(f"databricks {profile_flag} jobs list --output JSON", hide=True)
    run_status = json.loads(result.stdout)
    jobs = {e["settings"]["name"]: e["job_id"] for e in run_status["jobs"]}
    return jobs


def create_or_reset_job(
    json_payload: Dict[str, Any], profile: Optional[str] = None, job_id: Optional[str] = None
) -> Any:
    """Create or Reset a Databricks Job definition.

    - Takes a parsed JSON payload dictionary,
    - Encodes it into a temporary JSON file
    - Runs the `create` or `reset` command depending on the presence of `job_id`
    - cleans up temporary file
    - returns response

    Payload must comply with:
    https://docs.databricks.com/dev-tools/api/latest/jobs.html#
    """
    profile_flag = f"--profile {profile}" if profile else ""
    json_filename = "temp_job_file.json"
    if os.path.exists(json_filename):
        os.remove(json_filename)

    with open(json_filename, "w") as f:
        json.dump(json_payload, f)

    if job_id:
        result = invoke.run(f"databricks {profile_flag} jobs reset --job-id {job_id} --json-file {json_filename}")
    else:
        result = invoke.run(f"databricks {profile_flag} jobs create --json-file {json_filename}")

    os.remove(json_filename)
    return result.stdout


def wait_for_run_status(
    c: invoke.Context,
    profile: Optional[str],
    run_id: Optional[str],
    target_status: List[str] = ["TERMINATED"],
    failure_status: List[str] = ["INTERNAL_ERROR", "SKIPPED"],
) -> None:
    """Poll run status until in desired state."""
    profile_flag = f"--profile {profile}" if profile else ""
    current_status = None
    url = None
    run_status = {}

    while current_status not in target_status:
        result = c.run(f"databricks {profile_flag} runs get --run-id {run_id}", hide=True)
        run_status = json.loads(result.stdout)
        if url is None:
            url = run_status["run_page_url"]
            # print(url)

        current_status = run_status["state"]["life_cycle_state"]
        # print(current_status)
        if current_status in failure_status:
            raise ValueError(f"Run entered failed state {current_status}... aborting.")

        time.sleep(POLL_DELAY)

    # TODO: convert to logger output
    pp(run_status["state"])
    # print(url)
    # result = c.run(f"databricks {profile_flag} runs get-output --run-id {run_id}", hide=True)
    # output = json.loads(result.stdout)

    # TODO: show error output

    # for k in ["error", "error_trace", "logs"]:
    #     if k in output:
    #         print(f"\n========{k.upper()}======\n")
    #         print("\n".join(output[k].split("\\n")))
