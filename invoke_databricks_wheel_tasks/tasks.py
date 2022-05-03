# Standard Library
import json
from pprint import pprint as pp

# Third Party
from invoke import task

from .utils.databricks import (
    check_conf,
    create_or_reset_job,
    default_dbfs_artifact_path,
    default_dbfs_wheel_path,
    list_jobs,
    wait_for_cluster_status,
    wait_for_library_status,
    wait_for_run_status,
)
from .utils.misc import dict_from_keyvalue_list, load_config, merge_template, tidy

# NOTE: Invoke tasks files don't support mypy typechecking for the forseeable future
# They were looking at addressing it after Python2 EOL 01-01-2020 but there was a global pandemic.
# https://github.com/pyinvoke/invoke/issues/357

POLL_DELAY = 5


@task
def upload(c, profile=None, artifact_path=None, branch_name=None):
    """Upload wheel artifact to DBFS."""
    profile = check_conf(c, profile, "databricks.profile")
    profile_flag = f"--profile {profile}" if profile else ""

    artifact_path = check_conf(c, artifact_path, "databricks.artifact-path", should_raise=False)
    if artifact_path is None:
        artifact_path = default_dbfs_artifact_path(branch_name)

    print(f"Copying from dist/ --> '{artifact_path}' recursively...")
    c.run(f"dbfs {profile_flag} cp -r dist/ {artifact_path} --overwrite")

    c.run(f"dbfs {profile_flag} ls {artifact_path}")


@task
def clean(c, profile=None, artifact_path=None, branch_name=None):
    """Clean wheel artifact from DBFS."""
    profile = check_conf(c, profile, "databricks.profile")
    profile_flag = f"--profile {profile}" if profile else ""

    artifact_path = check_conf(c, artifact_path, "databricks.artifact-path", should_raise=False)
    if artifact_path is None:
        artifact_path = default_dbfs_artifact_path(branch_name)

    print(f"Deleting from '{artifact_path}' recursively...")
    c.run(f"dbfs {profile_flag} rm -r {artifact_path}")


@task
def reinstall(c, profile=None, cluster_id=None, wheel=None, branch_name=None):
    """Reinstall version of wheel on cluster with a restart."""
    profile = check_conf(c, profile, "databricks.profile")
    profile_flag = f"--profile {profile}" if profile else ""
    cluster_id = check_conf(c, cluster_id, "databricks.cluster-id")
    wheel = check_conf(c, wheel, "databricks.wheel", should_raise=False)
    if wheel is None:
        wheel = default_dbfs_wheel_path(branch_name)

    print(wheel)

    # Remove from 'libraries' and restart cluster
    c.run(f"databricks {profile_flag} libraries uninstall --cluster-id {cluster_id} --whl '{wheel}'")
    c.run(f"databricks {profile_flag} clusters restart --cluster-id {cluster_id}")
    wait_for_cluster_status(c, profile, cluster_id)

    # Reinstall updated wheel into clean restarted cluster
    c.run(f"databricks {profile_flag} libraries install --cluster-id {cluster_id} --whl '{wheel}'")
    wait_for_library_status(c, profile, cluster_id, wheel)


@task(
    iterable=["environment_variable"],
    help={
        "jinja_template": "Path to a valid Jinja2 template file",
        "config_file": tidy(
            """Either a JSON or YAML file that can be parsed and sent to the Jinja2 template engine.
            This is purely meant to be a configuration data structure.
            This file itself can be a Jinja2 template so that values from `environment_variables` can be injected.
        """
        ),
        "environment_variable": tidy(
            """Runtime environment variables to inject into `config_file`
        that can't be known ahead of time. Can be used repeatedly to specify many values. Eg `-e foo=bar -e fez=baz`.
        """
        ),
        "profile": "Optional databricks-cli profile name",
    },
)
def define_job(c, jinja_template, config_file, environment_variable=None, profile=None):
    """Generate templated Job definition and upsert by Job Name in template.

    It is left to the user to define their own datastructures for config_file,
    and make use of the looping and conditional constructs in Jinja2 to iterate
    over those constructs.
    """
    profile = check_conf(c, profile, "databricks.profile")

    env = dict_from_keyvalue_list(environment_variable)
    conf = load_config(config_file, env)
    jobs = list_jobs(profile)
    job_id = jobs[conf["name"]] if conf["name"] in jobs else None
    if job_id:
        conf["job_id"] = job_id

    merged_template = merge_template(jinja_template, conf)
    parsed_content = json.loads(merged_template)
    result = create_or_reset_job(parsed_content, profile=profile, job_id=job_id)
    pp(result)


@task
def runjob(c, profile=None, job_id=None):
    """Trigger default job associated for this project."""
    profile = check_conf(c, profile, "databricks.profile")
    profile_flag = f"--profile {profile}" if profile else ""
    job_id = check_conf(c, job_id, "databricks.job-id")

    result = c.run(f"databricks {profile_flag} jobs run-now --job-id {job_id}", hide=True)
    run_id = json.loads(result.stdout)["run_id"]
    wait_for_run_status(c, profile, run_id)
