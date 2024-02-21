# Report for assignment 3

This is a template for your report. You are free to modify it as needed.
It is not required to use markdown for your report either, but the report
has to be delivered in a standard, cross-platform format.

## Project

Name: PDM

URL: https://github.com/pdm-project/pdm

A package manager for python projects.

## Onboarding experience

Did it build and run as documented?
    
See the assignment for details; if everything works out of the box,
there is no need to write much here. If the first project(s) you picked
ended up being unsuitable, you can describe the "onboarding experience"
for each project, along with reason(s) why you changed to a different one.

PDM was the first project we picked.

The project has a good CONTRIBUTING.md, where clear instructions are given
on how to organize ones contribution. The project recomends using it's own 
product (PDM) to ensure formatting and linting. Changes are documented using 
`news` fragments. 


## Complexity

1. What are your results for ten complex functions?
   * Did all methods (tools vs. manual count) get the same result?
   * Are the results clear?
2. Are the functions just complex, or also long?
3. What is the purpose of the functions?
4. Are exceptions taken into account in the given measurements?
5. Is the documentation clear w.r.t. all the possible outcomes?

## Refactoring

Plan for refactoring complex code:

Estimated impact of refactoring (lower CC, but other drawbacks?).

Carried out refactoring (optional, P+):

git diff ...

## Coverage

### Tools

Document your experience in using a "new"/different coverage tool.

How well was the tool documented? Was it possible/easy/difficult to
integrate it with your build environment?

### Your own coverage tool

Show a patch (or link to a branch) that shows the instrumented code to
gather coverage measurements.

The patch is probably too long to be copied here, so please add
the git command that is used to obtain the patch instead:

git diff ...

What kinds of constructs does your tool support, and how accurate is
its output?

### Evaluation

1. How detailed is your coverage measurement?

2. What are the limitations of your own tool?

3. Are the results of your tool consistent with existing coverage tools?

## Coverage improvement

### Requirements

Here are the identified requirements for the given test suites. To put these in context would require seeing the commits that they belong to. These can be found here:
1. [do_update](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/338aa3fc6313c5f1d644b4fc5ee61703c0f1336c)
2. [_merge_bounds_and_excludes](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/9f0223b066b65b39a71f21a6a6a9d8fe1ccc799c)
3. [synchronize](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/f995337e29778c75c3b1144b94c9af1243229ed5)
4. [clean_metadata](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/f1c823f481cc8fe0230c56b4dfddb24f87bb6dc3)
5. [_build_pyspec_from_marker](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/387b0b2044aa3107138327e03a1193177f7084a1)

#### do_update
For the very high complexity of do_update, the tests cover quite 
a lot. A few branches are not tested though, these are: 
   1. When no HookManager (arg: hooks = None) is given.
       This is probably something worth testing, as a new 
       HookManager instance is created when it is not provided.
       However, `do_update` is only called from the sibling
       method `handle`, which explicitly creates a HookManager.
       So it is unclear when this argument will be None.
   2. When there are locked groups, but one of the given 
       selection of groups are not in the lock.
       There is a test `test_update_group_not_in_lockfile`
       which almost covers this, but that exception gets thrown 
       in `filters.py`. And is not the exception in `do_update`
       as you might expect.

#### _merge_bounds_and_excludes
The test requirements do not include versions outside of bounds [lower, upper], 
some normalization of operator specifiers, invalid operation specifiers, 
invalid PySpecSet parameters, tests for is_allow_all(), or tests for the 
__eq__ operator. 

### synchronize
* Test 1: When removing a package from the working set it should not affect the lock file of the virtual environment.
Thus this test checks the special branch in the remove distribution function where if the package is in the lock file it should
only be removed from the working set dict not the lock file.

* Test 2: When removing a non-existing package from a project it should result in an error code 1 from the try and except test when removing
a package. Other tests test exit codes from other branches in the synchronize module but not this specific case with the lock file.

* Test 3: When updating a package in a project it should not automatically update the lockfile until this is
explicitly requested (package version in lockfile should remain). The working set is however updated (package version is updated). 
This specific branch is tested below where the asserts check the version number.

* Test 4: When updating a group of dependencies the try except block should return a non-zero exit code along with keeping the packages
in the lockfile. Packages that don't belong to that group and are not installed should not be updated.

### clean_metadata
There were no already existing requirements for the function
`clean_metadata`. The tests that have been added directly tests
four branches and by extension two other branches due to the
logic of the function. The branches are more specifically when
the input metadata contains an:
1. `author` key.
2. `author_email` key.
3. `maintainer` key.
4. `maintainer_email` key.
If there is an `author` or `author_email` key, another branch
`if author` will also be executed. Similarly, if there is an
`maintainer` or `maintainer_email` key, another branch
`if maintainer:` will be executed.
6 branches are covered with these tests.

### _build_pyspec_from_marker
The tests test that 
* _build_pyspec_from_marker of MultiMarker with unsupported marker type raises TypeError
* _build_pyspec_from_marker of MarkerUnion with unsupported marker type raises TypeError
* get_marker of an invalid marker string raises RequirementError
* get_marker of Marker instance returns a Marker with the same string representation
The tests enters branches of the functions _build_pyspec_from_marker and get_marker that 
were not covered previously. 

Report of old coverage: [link to the old coverage](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/blob/snapshot-complexity-coverage/coverage.txt)

| File | Coverage | Function|
| --- | ----------- | ---|
| src/pdm/cli/commands/update.py | 95% | do_update|
| src/pdm/models/specifiers.py | 83% | _merge_bounds_and_excludes|
|src/pdm/installers/synchronizers.py | 80%| synchronize|
|src/pdm/models/in_process/parse_setup.py | 0%| clean_metadata|
|pdm/models/markers.py| 82% |_build_pyspec_from_marker


Report of new coverage: [link]

| File | Coverage | Function |
| ---------| ---------|------|
|
|src/pdm/cli/commands/update.py| 99% | do_update|
|src/pdm/models/specifiers.py | 90%  | _merge_bounds_and_excludes|
|src/pdm/installers/synchronizers.py | 85% | synchronize|
|src/pdm/models/in_process/parse_setup.py | 22%| clean_metadata|
|pdm/models/markers.py| 91% |_build_pyspec_from_marker|


We added at least four test cases per team member. These can be seen in the commits below.
1. [do_update](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/338aa3fc6313c5f1d644b4fc5ee61703c0f1336c)
2. [_merge_bounds_and_excludes](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/9f0223b066b65b39a71f21a6a6a9d8fe1ccc799c)
3. [synchronize](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/f995337e29778c75c3b1144b94c9af1243229ed5)
4. [clean_metadata](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/f1c823f481cc8fe0230c56b4dfddb24f87bb6dc3)
5. [_build_pyspec_from_marker](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/387b0b2044aa3107138327e03a1193177f7084a1)

## Self-assessment: Way of working

Current state according to the Essence standard: ...

Was the self-assessment unanimous? Any doubts about certain items?

How have you improved so far?

Where is potential for improvement?

## Overall experience

What are your main take-aways from this project? What did you learn?

Is there something special you want to mention here?
