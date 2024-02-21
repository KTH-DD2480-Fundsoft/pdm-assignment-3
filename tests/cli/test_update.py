import pytest

from pdm.models.requirements import parse_requirement


######################### NEW TESTS ########################
'''
For the very high complexity of do_update, the tests cover quite 
a lot. A few branches are not tested though, these are: 
    1. When no HookManager (arg: hooks = None) is given.
       This is probably something worth testing, as a new 
       HookManager instance is created when it is not provided.
       However, `do_update` is only called from the sibling
       method `handle`, which explicitly creates a HookManager.
       So it is unclear when this argument will be None.
'''
'''
    2. When there are locked groups, but one of the given 
       selection of groups are not in the lock.
       There is a test `test_update_group_not_in_lockfile`
       which almost covers this, but that exception gets thrown 
       in `filters.py`. And is not the exception in `do_update`
       as you might expect.
'''
def test_update_group_not_in_lock(project, pdm):
    pdm(["add", "pytz", "--group", "extra1"]
        , obj=project, strict=True)
    project.lockfile.groups.pop() 
    result = pdm(["update", "pytz", "--group", "extra1"]
                 , obj=project)
    assert "Requested group not in lockfile: extra1" in result.stderr

'''
    3. When a package is not present as a dependecy in its 
       own group, both for dev-groups and non-dev-groups 
'''
@pytest.mark.usefixtures("working_set")
def test_update_missing_dev_group_deps(project, pdm):
    pdm(["add", "requests", "-d"], obj=project, strict=True)
    project.pyproject.settings.setdefault("dev-dependencies",{})["dev"] = [] 
    result = pdm(["update", "requests", "-d"], obj=project)
    assert "requests does not exist in dev dev-dependencies." in result.stderr

@pytest.mark.usefixtures("working_set")
def test_update_missing_group_deps(project, pdm):
    pdm(["add", "requests", "--group", "extra1"], obj=project, strict=True)
    project.pyproject.metadata["dependencies"] = []
    result = pdm(["update", "requests"], obj=project)
    assert "requests does not exist in default dependencies." in result.stderr
'''    
    4. Related to #3; there is a list comprehension filtering
       out dependencies whose group is not in the lockfile.
       This branch will be taken when there is a dependency
       whose group is not in the lockfile, but when this dep 
       is not the one being updated. In other words, do_update 
       does not add groups to the lockfile which are not there 
       in the first place.
'''
def test_group_not_in_lock(project, pdm):
    pdm(["add", "pytz", "--group", "extra1"]
        , obj=project, strict=True)
    pdm(["add", "requests", "--group", "extra2"]
        , obj=project, strict=True)
    project.lockfile.groups.pop() 
    pdm(["update", "pytz", "--group", "extra1"]
        , obj=project, strict=True)
    assert "extra2" not in project.lockfile.groups 

######################### END NEW TESTS ########################

''' 
    Checks that the update command yields an exception when passing
    an argument to a non argument-taking flag (--top) 
'''
@pytest.mark.usefixtures("working_set")
def test_update_packages_with_top(project, pdm):
    pdm(["add", "requests"], obj=project, strict=True)
    result = pdm(["update", "--top", "requests"], obj=project)
    assert "PdmUsageError" in result.stderr

''' 
    Creates a mock of do_update, then calls the function via the pdm 
    interface and asserts that the function is only called once.
'''
def test_update_command(project, pdm, mocker):
    do_update = mocker.patch("pdm.cli.commands.update.Command.do_update")
    pdm(["update"], obj=project)
    do_update.assert_called_once()


''' 
    Ensures that a requirement is not updated without specifying
    new version(?), unless --unconstrained is used.
'''
@pytest.mark.usefixtures("working_set")
def test_update_ignore_constraints(project, repository, pdm):
    project.project_config["strategy.save"] = "compatible"
    pdm(["add", "pytz"], obj=project, strict=True)
    assert project.pyproject.metadata["dependencies"] == ["pytz~=2019.3"]
    repository.add_candidate("pytz", "2020.2")

    pdm(["update", "pytz"], obj=project, strict=True)
    assert project.pyproject.metadata["dependencies"] == ["pytz~=2019.3"]
    assert project.locked_repository.all_candidates["pytz"].version == "2019.3"

    pdm(["update", "pytz", "--unconstrained"], obj=project, strict=True)
    assert project.pyproject.metadata["dependencies"] == ["pytz~=2020.2"]
    assert project.locked_repository.all_candidates["pytz"].version == "2020.2"

''' 
    Ensure that all packages are updated when flag --update-all
    is used, and that locked dependencies are kept when flag 
    --update-reuse is used.
'''
@pytest.mark.usefixtures("working_set")
@pytest.mark.parametrize("strategy", ["reuse", "all"])
def test_update_all_packages(project, repository, pdm, strategy):
    pdm(["add", "requests", "pytz"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    repository.add_candidate("chardet", "3.0.5")
    repository.add_candidate("requests", "2.20.0")
    repository.add_dependencies(
        "requests",
        "2.20.0",
        [
            "certifi>=2017.4.17",
            "chardet<3.1.0,>=3.0.2",
            "idna<2.8,>=2.5",
            "urllib3<1.24,>=1.21.1",
        ],
    )
    result = pdm(["update", f"--update-{strategy}"], obj=project, strict=True)
    locked_candidates = project.locked_repository.all_candidates
    assert locked_candidates["requests"].version == "2.20.0"
    assert locked_candidates["chardet"].version == ("3.0.5" if strategy == "all" else "3.0.4")
    assert locked_candidates["pytz"].version == "2019.6"
    update_num = 3 if strategy == "all" else 2
    assert f"{update_num} to update" in result.stdout, result.stdout

    result = pdm(["sync"], obj=project, strict=True)
    assert "All packages are synced to date" in result.stdout

''' 
    Test that the updates with --frozen-lockfile flag does not keep 
    any updates, i.e. that it does not touch the lockfile.
'''
def test_update_no_lock(project, working_set, repository, pdm):
    pdm(["add", "pytz"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    pdm(["update", "--frozen-lockfile"], obj=project, strict=True)
    assert working_set["pytz"].version == "2019.6"
    project.lockfile.reload()
    assert project.locked_repository.all_candidates["pytz"].version == "2019.3"

'''
    Ensure that --dry-run flag does not change anything. That it 
    does not update any dependencies, but that it prints the 
    would-be updates.
'''
@pytest.mark.usefixtures("working_set")
def test_update_dry_run(project, repository, pdm):
    pdm(["add", "requests", "pytz"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    repository.add_candidate("chardet", "3.0.5")
    repository.add_candidate("requests", "2.20.0")
    repository.add_dependencies(
        "requests",
        "2.20.0",
        [
            "certifi>=2017.4.17",
            "chardet<3.1.0,>=3.0.2",
            "idna<2.8,>=2.5",
            "urllib3<1.24,>=1.21.1",
        ],
    )
    result = pdm(["update", "--dry-run"], obj=project, strict=True)
    project.lockfile.reload()
    locked_candidates = project.locked_repository.all_candidates
    assert locked_candidates["requests"].version == "2.19.1"
    assert locked_candidates["chardet"].version == "3.0.4"
    assert locked_candidates["pytz"].version == "2019.3"
    assert "requests 2.19.1 -> 2.20.0" in result.stdout

''' 
    Test --top with --dry-run. Dry run should only show updates 
    at the top level-- not transitive deps.
'''
@pytest.mark.usefixtures("working_set")
def test_update_top_packages_dry_run(project, repository, pdm):
    pdm(["add", "requests", "pytz"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    repository.add_candidate("chardet", "3.0.5")
    repository.add_candidate("requests", "2.20.0")
    repository.add_dependencies(
        "requests",
        "2.20.0",
        [
            "certifi>=2017.4.17",
            "chardet<3.1.0,>=3.0.2",
            "idna<2.8,>=2.5",
            "urllib3<1.24,>=1.21.1",
        ],
    )
    result = pdm(["update", "--dry-run", "--top"], obj=project, strict=True)
    assert "requests 2.19.1 -> 2.20.0" in result.stdout
    assert "- chardet 3.0.4 -> 3.0.5" not in result.stdout


''' 
    Ensure that update [package] updates [package] and that it 
    does not update any dependencies when not needed.
'''
@pytest.mark.usefixtures("working_set")
def test_update_specified_packages(project, repository, pdm):
    pdm(["add", "requests", "pytz", "--no-sync"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    repository.add_candidate("chardet", "3.0.5")
    repository.add_candidate("requests", "2.20.0")
    repository.add_dependencies(
        "requests",
        "2.20.0",
        [
            "certifi>=2017.4.17",
            "chardet<3.1.0,>=3.0.2",
            "idna<2.8,>=2.5",
            "urllib3<1.24,>=1.21.1",
        ],
    )
    pdm(["update", "requests"], obj=project, strict=True)
    locked_candidates = project.locked_repository.all_candidates
    assert locked_candidates["requests"].version == "2.20.0"
    assert locked_candidates["chardet"].version == "3.0.4"

''' 
    Ensure that the eager mode flag updates dependencies of a package 
    that are available. But does not touch unmentioned deps.
'''
@pytest.mark.usefixtures("working_set")
def test_update_specified_packages_eager_mode(project, repository, pdm):
    pdm(["add", "requests", "pytz", "--no-sync"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    repository.add_candidate("chardet", "3.0.5")
    repository.add_candidate("requests", "2.20.0")
    repository.add_dependencies(
        "requests",
        "2.20.0",
        [
            "certifi>=2017.4.17",
            "chardet<3.1.0,>=3.0.2",
            "idna<2.8,>=2.5",
            "urllib3<1.24,>=1.21.1",
        ],
    )
    pdm(["update", "requests", "--update-eager"], obj=project, strict=True)
    locked_candidates = project.locked_repository.all_candidates
    assert locked_candidates["requests"].version == "2.20.0"
    assert locked_candidates["chardet"].version == "3.0.5"
    assert locked_candidates["pytz"].version == "2019.3"

''' 
    Ensure that the eager mode config setting updates dependencies of a package 
    that are available. But does not touch unmentioned deps.
'''
@pytest.mark.usefixtures("working_set")
def test_update_specified_packages_eager_mode_config(project, repository, pdm):
    pdm(["add", "requests", "pytz", "--no-sync"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    repository.add_candidate("chardet", "3.0.5")
    repository.add_candidate("requests", "2.20.0")
    repository.add_dependencies(
        "requests",
        "2.20.0",
        [
            "certifi>=2017.4.17",
            "chardet<3.1.0,>=3.0.2",
            "idna<2.8,>=2.5",
            "urllib3<1.24,>=1.21.1",
        ],
    )
    pdm(["config", "strategy.update", "eager"], obj=project, strict=True)
    pdm(["update", "requests"], obj=project, strict=True)
    locked_candidates = project.locked_repository.all_candidates
    assert locked_candidates["requests"].version == "2.20.0"
    assert locked_candidates["chardet"].version == "3.0.5"
    assert locked_candidates["pytz"].version == "2019.3"


''' 
    Ensure that updating with both package name and group name 
    throws an error.
'''
@pytest.mark.usefixtures("working_set")
def test_update_with_package_and_groups_argument(project, pdm):
    pdm(["add", "-G", "web", "requests"], obj=project, strict=True)
    pdm(["add", "-Gextra", "pytz"], obj=project, strict=True)
    result = pdm(["update", "requests", "--group", "web", "-G", "extra"], obj=project)
    assert "PdmUsageError" in result.stderr

    result = pdm(["update", "requests", "--no-default"], obj=project)
    assert "PdmUsageError" in result.stderr


'''
    Ensure that the flag --prerelease throws an error when not given 
    a package name.
'''
@pytest.mark.usefixtures("working_set")
def test_update_with_prerelease_without_package_argument(project, pdm):
    pdm(["add", "requests"], obj=project, strict=True)
    result = pdm(["update", "--prerelease"], obj=project)
    assert "--prerelease/--stable must be used with packages given" in result.stderr


''' 
    Ensure:
        that compatible versions are saved across updates,
        that prereleases are kept across update 
        that --stable resets to stable version 
        that --prerelease --unconstrained picks the latest prerelease 
'''
def test_update_existing_package_with_prerelease(project, working_set, pdm):
    project.project_config["strategy.save"] = "compatible"
    pdm(["add", "urllib3"], obj=project, strict=True)
    assert project.pyproject.metadata["dependencies"][0] == "urllib3~=1.22"
    assert working_set["urllib3"].version == "1.22"

    pdm(["update", "urllib3", "--prerelease"], obj=project, strict=True)
    assert project.pyproject.metadata["dependencies"][0] == "urllib3~=1.22"
    assert working_set["urllib3"].version == "1.23b0"

    pdm(["update", "urllib3"], obj=project, strict=True)  # prereleases should be kept
    assert working_set["urllib3"].version == "1.23b0"

    pdm(["update", "urllib3", "--stable"], obj=project, strict=True)
    assert working_set["urllib3"].version == "1.22"

    pdm(["update", "urllib3", "--prerelease", "--unconstrained"], obj=project, strict=True)
    assert project.pyproject.metadata["dependencies"][0] == "urllib3<2,>=1.23b0"
    assert working_set["urllib3"].version == "1.23b0"

''' 
    check that updating a package is updated automatically
    if all extra reqs are met.
''' 
def test_update_package_with_extras(project, repository, working_set, pdm):
    repository.add_candidate("foo", "0.1")
    foo_deps = ["urllib3; extra == 'req'"]
    repository.add_dependencies("foo", "0.1", foo_deps)
    pdm(["add", "foo[req]"], obj=project, strict=True)
    assert working_set["foo"].version == "0.1"

    repository.add_candidate("foo", "0.2")
    repository.add_dependencies("foo", "0.2", foo_deps)
    pdm(["update"], obj=project, strict=True)
    assert working_set["foo"].version == "0.2"
    assert project.locked_repository.all_candidates["foo"].version == "0.2"


'''
    Ensure that update groups updates members.
'''
def test_update_groups_in_lockfile(project, working_set, pdm, repository):
    pdm(["add", "requests"], obj=project, strict=True)
    repository.add_candidate("foo", "0.1")
    pdm(["add", "foo", "--group", "extra"], obj=project, strict=True)
    assert project.lockfile.groups == ["default", "extra"]
    repository.add_candidate("foo", "0.2")
    pdm(["update"], obj=project, strict=True)
    assert project.locked_repository.all_candidates["foo"].version == "0.2"
    assert working_set["foo"].version == "0.2"

''' 
    Ensure updating group not present in lockfile throws error.
'''
def test_update_group_not_in_lockfile(project, working_set, pdm):
    pdm(["add", "requests"], obj=project, strict=True)
    project.add_dependencies({"pytz": parse_requirement("pytz")}, to_group="extra")
    result = pdm(["update", "--group", "extra"], obj=project)
    assert result.exit_code != 0
    assert "Requested groups not in lockfile: extra" in result.stderr

####################### New Tests #######################
'''
These new tetsts aim to improve branch and path coverage for the functions in the `synchronizer` class. These tests slightly improve
coverage for various subfunctions of the class which aim to resolve specific test conditions omitted by previous tests. Tests should benefit
other files as well but this is however not tested.
'''

'''
When updating a package in a project it should not automatically update the lockfile until this is 
explicitly requested (package version in lockfile should remain). The working set is however updated (package version is updated). 
This specific branch is tested below where the asserts check the version number.
'''
def test_update_package_lock(project, working_set, repository, pdm):
    """
    Test case checks that packages can be added to the project and repository and later updated to a newer version without affecting the 
    project lock file.
    """
    pdm(["add", "pytz"], obj=project, strict=True)
    repository.add_candidate("pytz", "2019.6")
    pdm(["update", "--frozen-lockfile"], obj=project, strict=True)
    assert working_set["pytz"].version == "2019.6"
    project.lockfile.reload()
    assert project.locked_repository.all_candidates["pytz"].version == "2019.3"

'''
When updating a group of dependencies the try except block should return a non-zero exit code along with keeping the packages
in the lockfile. Packages that don't belong to that group and are not installed should not be updated.

'''
def test_update_groups_and_lock(project, pdm, working_set):
    """
    Test case checks that packages can be added to a certain group and then be able to update that group without error. Asserts correct 
    exit codes, that packages are in correct set and in the correct locked file.
    """
    project.add_dependencies({"urllib3": parse_requirement("urllib3")})
    project.add_dependencies({"pytz": parse_requirement("pytz")}, to_group="tz")
    project.add_dependencies({"requests": parse_requirement("pytz")}, to_group="tz")
    pdm(["install", "-Gtz", "--no-default"], obj=project, strict=True)
    result = pdm(["update", "--group", "tz"], obj=project)
    assert result.exit_code != 0
    assert "pytz" in working_set
    assert "urllib3" not in working_set
    assert project.lockfile.groups == ["tz"]
    assert "pytz" in project.locked_repository.all_candidates
    assert "urllib3" not in project.locked_repository.all_candidates

####################### End Tests #######################