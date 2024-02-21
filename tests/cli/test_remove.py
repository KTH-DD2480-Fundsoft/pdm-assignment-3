import pytest

from pdm.cli import actions
from pdm.models.requirements import parse_requirement
from pdm.models.specifiers import PySpecSet


def test_remove_command(project, pdm, mocker):
    do_remove = mocker.patch("pdm.cli.commands.remove.Command.do_remove")
    pdm(["remove", "demo"], obj=project)
    do_remove.assert_called_once()


@pytest.mark.usefixtures("working_set", "vcs")
def test_remove_editable_packages_while_keeping_normal(project, pdm):
    project.environment.python_requires = PySpecSet(">=3.6")
    pdm(["add", "demo"], obj=project, strict=True)
    pdm(["add", "-d", "-e", "git+https://github.com/test-root/demo.git#egg=demo"], obj=project, strict=True)
    dev_group = project.pyproject.settings["dev-dependencies"]["dev"]
    default_group = project.pyproject.metadata["dependencies"]
    pdm(["remove", "-d", "demo"], obj=project, strict=True)
    assert not dev_group
    assert len(default_group) == 1
    assert not project.locked_repository.all_candidates["demo"].req.editable


def test_remove_package(project, working_set, dev_option, pdm):
    pdm(["add", *dev_option, "requests", "pytz"], obj=project, strict=True)
    pdm(["remove", *dev_option, "pytz"], obj=project, strict=True)
    locked_candidates = project.locked_repository.all_candidates
    assert "pytz" not in locked_candidates
    assert "pytz" not in working_set


def test_remove_package_no_lock(project, working_set, dev_option, pdm):
    pdm(["add", *dev_option, "requests", "pytz"], obj=project, strict=True)
    pdm(["remove", *dev_option, "--frozen-lockfile", "pytz"], obj=project, strict=True)
    assert "pytz" not in working_set
    project.lockfile.reload()
    locked_candidates = project.locked_repository.all_candidates
    assert "pytz" in locked_candidates


def test_remove_package_with_dry_run(project, working_set, pdm):
    pdm(["add", "requests"], obj=project, strict=True)
    result = pdm(["remove", "requests", "--dry-run"], obj=project, strict=True)
    project._lockfile = None
    locked_candidates = project.locked_repository.all_candidates
    assert "urllib3" in locked_candidates
    assert "urllib3" in working_set
    assert "- urllib3 1.22" in result.output


def test_remove_package_no_sync(project, working_set, pdm):
    pdm(["add", "requests", "pytz"], obj=project, strict=True)
    pdm(["remove", "pytz", "--no-sync"], obj=project, strict=True)
    locked_candidates = project.locked_repository.all_candidates
    assert "pytz" not in locked_candidates
    assert "pytz" in working_set


@pytest.mark.usefixtures("working_set")
def test_remove_package_not_exist(project, pdm):
    pdm(["add", "requests", "pytz"], obj=project, strict=True)
    result = pdm(["remove", "django"], obj=project)
    assert result.exit_code == 1


def test_remove_package_exist_in_multi_groups(project, working_set, pdm):
    pdm(["add", "requests"], obj=project, strict=True)
    pdm(["add", "--dev", "urllib3"], obj=project, strict=True)
    pdm(["remove", "--dev", "urllib3"], obj=project, strict=True)
    assert all("urllib3" not in line for line in project.pyproject.settings["dev-dependencies"]["dev"])
    assert "urllib3" in working_set
    assert "requests" in working_set


@pytest.mark.usefixtures("repository")
def test_remove_no_package(project, pdm):
    result = pdm(["remove"], obj=project)
    assert result.exit_code != 0


@pytest.mark.usefixtures("working_set")
def test_remove_package_wont_break_toml(project_no_init, pdm):
    project_no_init.pyproject._path.write_text(
        """
[project]
dependencies = [
    "requests",
    # this is a comment
]
"""
    )
    project_no_init.pyproject.reload()
    pdm(["remove", "requests"], obj=project_no_init, strict=True)
    assert project_no_init.pyproject.metadata["dependencies"] == []


@pytest.mark.usefixtures("working_set")
def test_remove_group_not_in_lockfile(project, pdm, mocker):
    pdm(["add", "requests"], obj=project, strict=True)
    project.add_dependencies({"pytz": parse_requirement("pytz")}, to_group="tz")
    assert project.lockfile.groups == ["default"]
    locker = mocker.patch.object(actions, "do_lock")
    pdm(["remove", "--group", "tz", "pytz"], obj=project, strict=True)
    assert not project.pyproject.metadata["optional-dependencies"].get("tz")
    locker.assert_not_called()

####################### New Tests #######################
'''
These new tetsts aim to improve branch and path coverage for the functions in the `synchronizer` class. These tests slightly improve
coverage for various subfunctions of the class which aim to resolve specific test conditions omitted by previous tests. Tests should benefit
other files as well but this is however not tested.

More specifically: 
The synchronizer module is quite well tested but still lacks some exception handling along with tests for removing packages 
from the pdm lock file. 
'''

'''
When removing a package from the working set it should not affect the lock file of the virtual environment. 
Thus this test checks the special branch in the remove distribution function where if the package is in the lock file it should
only be removed from the working set dict not the lock file.

'''
def test_remove_package_lock(project, working_set, dev_option, pdm):
    """
    Test case checks if it is possible to remove a package with the lock setting. Adds several packages and removes one with
    the frozen-lockfile setting. Checks that the package is still in lock file. 
    """
    pdm(["add", *dev_option, "requests", "requests"], obj=project, strict=True)
    pdm(["remove", *dev_option, "--frozen-lockfile", "requests"], obj=project, strict=True)
    assert "requests" not in working_set
    project.lockfile.reload()
    locked_candidates = project.locked_repository.all_candidates
    assert "requests" in locked_candidates

'''
When removing a non-existing package from a project it should result in an error code 1 from the try and except test when removing
a package. Other tests test exit codes from other branches in the synchronize module but not this specific case with the lock file.

'''
@pytest.mark.usefixtures("repository")
def test_remove_with_no_package_error(project, working_set, pdm):
    """
    Test checks that "remove" functionality is working with correct error and exit codes. Adds several packages, asserts that they're in 
    the correct folder, attempts to remove non-existing package as well as pop remove another package. Asserts that the exit.codes are 
    correct
    """
    pdm(["add", "pytz"], obj=project, strict=True)
    pdm(["add", "requests"], obj=project, strict=True)
    assert "pytz" in working_set
    assert "requests" in working_set
    assert "django" not in working_set
    result = pdm(["remove", "django"], obj=project)
    assert result.exit_code == 1
    result = pdm(["remove"], obj=project)
    assert result.exit_code != 0

####################### End Tests #######################