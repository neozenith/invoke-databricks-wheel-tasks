# Standard Library
import json
import time
from functools import lru_cache
from pprint import pprint as pp
from typing import List, Optional, Union

# Third Party
import invoke

from .git import git_current_branch
from .poetry import poetry_project_name, poetry_wheelname

POLL_DELAY = 5


@lru_cache(maxsize=None)
def default_dbfs_artifact_path() -> str:
    """Helper to construct a default artifact path to upload to in DBFS."""
    return f"dbfs:/FileStore/wheels/{poetry_project_name()}/{git_current_branch()}/"


@lru_cache(maxsize=None)
def default_dbfs_wheel_path() -> str:
    """Helper to construct a default artifact path to upload to in DBFS."""
    return f"{default_dbfs_artifact_path()}{poetry_wheelname()}"


def wait_for_cluster_status(
    c: invoke.Context,
    profile: Optional[str],
    cluster_id: Optional[str],
    target_status: List[str] = ["RUNNING"],
    failure_status: List[str] = [],
) -> None:
    """Poll cluster status until in desired state."""
    current_status = None
    while current_status not in target_status:
        result = c.run(
            f"databricks --profile {profile} clusters events --cluster-id {cluster_id} --output JSON", hide=True
        )
        latest_event = json.loads(result.stdout)["events"][0]
        pp(latest_event["type"])
        current_status = latest_event["type"]
        if current_status in failure_status:
            raise ValueError(f"Cluster entered failed state {current_status}... aborting.")

        time.sleep(POLL_DELAY)


def wait_for_library_status(
    c: invoke.Context,
    profile: Optional[str],
    cluster_id: Optional[str],
    wheel: Optional[str],
    target_status: List[str] = ["INSTALLED"],
    failure_status: List[str] = [],
) -> None:
    """Poll library statuses until target library in desired state."""
    current_status = None
    while current_status not in target_status:
        result = c.run(f"databricks --profile {profile} libraries cluster-status --cluster-id {cluster_id}", hide=True)
        statuses = json.loads(result.stdout)["library_statuses"]
        filtered_status = [
            status for status in statuses if "whl" in status["library"] and status["library"]["whl"] == wheel
        ]
        pp(filtered_status[0]["status"])
        current_status = filtered_status[0]["status"]
        if current_status in failure_status:
            raise ValueError(f"Library entered failed state {current_status}... aborting.")

        time.sleep(POLL_DELAY)


def wait_for_run_status(
    c: invoke.Context,
    profile: Optional[str],
    run_id: Optional[str],
    target_status: List[str] = ["TERMINATED"],
    failure_status: List[str] = ["INTERNAL_ERROR"],
) -> None:
    """Poll run status until in desired state."""
    current_status = None
    url = None
    run_status = {}
    while current_status not in target_status:
        result = c.run(f"databricks --profile {profile} runs get --run-id {run_id}", hide=True)
        run_status = json.loads(result.stdout)
        if url is None:
            url = run_status["run_page_url"]
            print(url)

        current_status = run_status["state"]["life_cycle_state"]
        print(current_status)
        if current_status in failure_status:
            raise ValueError(f"Run entered failed state {current_status}... aborting.")

        time.sleep(POLL_DELAY)

    pp(run_status["state"])
    print(url)
    result = c.run(f"databricks --profile {profile} runs get-output --run-id {run_id}", hide=True)
    output = json.loads(result.stdout)

    for k in ["error", "error_trace", "logs"]:
        if k in output:
            print(f"\n========{k.upper()}======\n")
            print("\n".join(output[k].split("\\n")))


def check_conf(
    c: invoke.Context, value: Optional[str], conf_key: str, should_raise: bool = True
) -> Optional[Union[invoke.Context, str]]:
    """Ensure a value is provided from CLI flag value or config."""
    if value is not None:
        return value

    key_parts = conf_key.split(".")
    output = c
    for part in key_parts:
        if part in output.keys() and output[part] is not None:
            output = output[part]
        else:
            if should_raise:
                # Insta-fail if key-path lookups fail
                raise ValueError(f"Could not resolve a non-null value from {conf_key} or required CLI flag.")
            else:
                return None

    # key-path lookups must have passed
    return output
