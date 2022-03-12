# Standard Library
import json

# Third Party
from invoke import task

from .utils import (
    check_conf,
    wait_for_cluster_status,
    wait_for_library_status,
    wait_for_run_status,
)

POLL_DELAY = 5


@task
def upload(c, profile=None, artifact_path=None):
    """Upload wheel artifact to DBFS."""
    profile = check_conf(c, profile, "databricks.profile")
    artifact_path = check_conf(c, artifact_path, "databricks.artifact-path")

    c.run(f"dbfs --profile {profile} rm -r {artifact_path}")
    c.run(f"dbfs --profile {profile} cp -r dist/ {artifact_path}")
    c.run(f"dbfs --profile {profile} ls {artifact_path}")


@task
def reinstall(c, profile=None, cluster_id=None, wheel=None):
    """Reinstall version of wheel on cluster with a restart."""
    profile = check_conf(c, profile, "databricks.profile")
    cluster_id = check_conf(c, cluster_id, "databricks.cluster-id")
    wheel = check_conf(c, wheel, "databricks.wheel")

    c.run(f"databricks --profile {profile} libraries uninstall --cluster-id {cluster_id} --whl '{wheel}'")
    c.run(f"databricks --profile {profile} clusters restart --cluster-id {cluster_id}")
    wait_for_cluster_status(c, profile, cluster_id)

    c.run(f"databricks --profile {profile} libraries install --cluster-id {cluster_id} --whl '{wheel}'")
    wait_for_library_status(c, profile, cluster_id, wheel)


@task
def runjob(c, profile=None, job_id=None):
    """Trigger default job associated for this project."""
    profile = check_conf(c, profile, "databricks.profile")
    job_id = check_conf(c, job_id, "databricks.job-id")

    result = c.run(f"databricks --profile {profile} jobs run-now --job-id {job_id}", hide=True)
    run_id = json.loads(result.stdout)["run_id"]
    wait_for_run_status(c, profile, run_id)
