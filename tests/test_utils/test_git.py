# Our Libraries
from invoke_databricks_wheel_tasks.utils.git import git_current_branch


def test_git_current_branch():
    # Given
    # .... mostly testing it doesn not throw an error from git API changes

    # When
    branch_name = git_current_branch()

    # Then
    assert branch_name != ""
    assert branch_name != "HEAD"
    assert len(branch_name) > 0
