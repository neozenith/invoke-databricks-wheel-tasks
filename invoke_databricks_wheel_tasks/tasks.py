# Standard Library
import json
from pprint import pprint as pp

# Third Party
from invoke import task

from .utils.databricks import (
    create_or_reset_job,
    default_dbfs_artifact_path,
    default_dbfs_wheel_path,
    list_jobs,
    wait_for_run_status,
)
from .utils.misc import dict_from_keyvalue_list, load_config, merge_template, tidy
from .utils.poetry import poetry_wheelname

# NOTE: Invoke tasks files don't support mypy typechecking for the forseeable future
# They were looking at addressing it after Python2 EOL 01-01-2020 but there was a global pandemic.
# https://github.com/pyinvoke/invoke/issues/357

POLL_DELAY = 5


@task
def poetry_wheel_name(c):
    """Display the name of the wheel file poetry would build."""
    print(poetry_wheelname())


@task
def dbfs_wheel_path(c, branch=None):
    """Generate the target path (including wheelname) this wheel should be uploaded to.

    Omitting branch will try to detect it, but in some CI systems you may need to inject this from an environment variable.
    """
    print(default_dbfs_wheel_path(branch))


@task
def dbfs_wheel_path_root(c, branch=None):
    """Generate the target path (excluding wheelname) this wheel should be uploaded to.

    Omitting branch will try to detect it, but in some CI systems you may need to inject this from an environment variable.
    """
    print(default_dbfs_artifact_path(branch))


@task
def upload(c, profile=None, artifact_path=None, branch_name=None):
    """Upload wheel artifact from dist to DBFS."""
    profile_flag = f"--profile {profile}" if profile else ""

    if artifact_path is None:
        artifact_path = default_dbfs_artifact_path(branch_name)

    print(f"Copying from dist/ --> '{artifact_path}' recursively...")
    c.run(f"dbfs {profile_flag} cp -r dist/ {artifact_path} --overwrite")

    c.run(f"dbfs {profile_flag} ls {artifact_path}")


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

    Example usage:
        $ invoke define-job \
            --jinja-template jobs/jaffleshop.json.j2 \
            --config jobs/jaffleshop.yml \
            -e my_wheel=$(invoke dbfs-wheel-path --branch $BRANCH) \
            -e branch=$BRANCH

    Some CI environments like Jenkins checkout exact commit hashes so branches
    are dangling but it stores the branch name in an environment variable
    we need to inject at runtime.
    """
    env = dict_from_keyvalue_list(environment_variable)
    conf = load_config(config_file, env)

    job_id = None  # Default to None and assume a new job needs to be created
    if "job_id" in conf:
        # Update a specific job_id that already exists specified in the config
        job_id = conf["job_id"]
    else:
        # Determine the job_id by looking up a job by name
        jobs = list_jobs(profile)
        job_id = jobs[conf["name"]] if conf["name"] in jobs else None
        if job_id:
            conf["job_id"] = job_id

    merged_template = merge_template(jinja_template, conf)
    parsed_content = json.loads(merged_template)
    result = create_or_reset_job(parsed_content, profile=profile, job_id=job_id)
    pp(result)


@task
def run_job(c, job_id, profile=None):
    """Trigger job based on job-id and wait.

    If you do not want to wait for the job to finish then just use the run-now CLI command.
    """
    profile_flag = f"--profile {profile}" if profile else ""

    result = c.run(f"databricks {profile_flag} jobs run-now --job-id {job_id}", hide=True)
    run_id = json.loads(result.stdout)["run_id"]
    wait_for_run_status(c, profile, run_id)
