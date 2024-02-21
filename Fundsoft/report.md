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

### 1. What are your results for five complex functions?
   * Did all methods (tools vs. manual count) get the same result?
   * Are the results clear?

Interestingly enough, we got the same result from a manual calculation and an automatic calculation (using Lizard) for just one function, `synchronize@385-467@./src/pdm/installers/synchronizers.py`. In three other cases, our manual calculations came out to be one or two points greater than the automatic ones. For the last function, `do_update@91-200@src/pdm/cli/commands/update.py`, we got a result that was two less than the one calculated by Lizard.

There was some disagreement about the CCNs among the members in the beginning. Each disagreement was resolved by the two people responsible for the function recalculating the CCN and together reaching a conclusion about what the CCN should be. We planned on having a third member ultimately deciding if the two people were still in disagreement. Fortunately, however, this did not occur.

More information about the manual calculations can be found [here](ccn_calculations/)


### 2. Are the functions just complex, or also long?

This really depends on the function. `_parse_setup_cfg` is only 60 lines long but still has a CCN of 28. Thus it is a very complex function but not a very long one. The other functions are both complex and long. `do_add_calculations` is 100 lines with a CCN of 36, `do_lock` is 93 lines with a CCN of 93, `do_update` is 110 lines with a CCN of 37, and `synchronize` is 80 lines with a CCN of 18.

### 3. What is the purpose of the functions?

#### Purpose of `_parse_setup_cfg`
`_parse_setup_cfg`is responsible for parsing a setup.cfg file. It extracts various metadata fields and stores them in a dictionary `result` that is returned. The function has many if-blocks and 60 NLOC according to Lizard.

#### Purpose of `do_lock`
Locking in a package manager means locking down the versions of the dependencies that are used in the project. `do_lock` does that locking as well as updating the lock file. It is quite a long function of about 100 lines which is a reason for its high CCN. Another reason for the high CCN is the error handling to do with logging.  

#### Purpose of `do_add`
`do_add` is the function that is run to add packages to the project, i.e. to `pyproject.toml`. The process of adding requirements requires checking dependecies (updating the lockfile, checking the dependency group), adding dependencies, and even parsing dependencies. The function also normalizes names and has different logic
depending on what flag is given to the command. The function has a lot of list comprehension, error checking, and different behaviour depending on flags which increases the complexity
quite a bit. 

#### Purpose of `do_update`
`do_update` is the function that is run to update the packages in `pyproject.toml`. Updating packages is a complicated task that requires much error handling which is one of the key reasons for the high CCN. The function checks for potential errors with rather complicated boolean expressions at four separate times which contributes immensely to the high CCN. The function is also rather long, about 100 lines, which also contributes to its high CCN. 

#### Purpose of `synchronize`
pdm is a package manager and includes several classes of `synchronizers` that take care of synching which packages to install, update or remove from the local environment. The `synchronize` function belongs to one of these classes and is used to decide which packages need to be installed or removed. More specifically the function compares the desired packages with the current working set through a helper function and creates a "to_do" dictionary that logs which packages need to be added, removed, or updated in the environment using the keys "add", "remove" or "update". It then splits these tasks into two lists: "sequential" and "parallel" tasks. It then iterates through all the tasks and attempts to complete them. If an installation fails then the function can either be set to continue with the remaining packages or break the installation depending on the users' input and preference. All of this together makes the function slightly complex including several different internal sections. The code doesn't include any obvious redundancies and is streamlined to its tasks, however, there is potential to split the function into smaller components that can be tested individually making it potentially easier to maintain and understand.

#### 4. Are exceptions taken into account in the given measurements?
We didn't find any reference to how Lizard does its CCN calculations. However, we found how Radon does its calculations (which can be found [here](https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity)) and Lizard and Radon give out roughly the same results for our functions (they sometimes differ by one). Radon takes exceptions into account by adding 1 for each except block in the code. We did the same in our manual calculations.

#### 5. Is the documentation clear w.r.t. all the possible outcomes?
The documentation is not very clear about all the possible outcomes. The comments in the code are sparse and don't contain much information at all. Furthermore, there aren't many comments describing what happens in the different branches. To fix this, the developers could add better docstrings that explain what each function does and what each parameter to each function does. This would make it easier to understand what happens at each branching point.

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

Show the comments that describe the requirements for the coverage.

Report of old coverage: [link]

Report of new coverage: [link]

Test cases added:

git diff ...

Number of test cases added: two per team member (P) or at least four (P+).

## Self-assessment: Way of working

Current state according to the Essence standard: ...

Was the self-assessment unanimous? Any doubts about certain items?

How have you improved so far?

Where is potential for improvement?

## Overall experience

What are your main take-aways from this project? What did you learn?

Is there something special you want to mention here?
