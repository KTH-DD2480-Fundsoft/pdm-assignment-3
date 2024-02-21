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

We looked at the open source project pdm which is a python package manager. The very nice thing with pdm was that it included its own coverage tool which made it the onboarding process very simple and easy. We simply had to run `pdm coverage` in our terminal to activate the coverage tool which then ran many tests. pdms GitHub repo also included some documentation on the current coverages of the different modules in the library which made it very easy to assess the coverage of the different functions and modules. This coverage.txt file also included which lines included missing branch coverage which made it very easy to "debug" where we needed to look in order to improve the branch coverage. As it was already built into the pdm repository it was very easy to integrate into our build environment.

### Your own coverage tool

Our own coverage tool works by manually adding lines at the beginning of each branch that correspond to a certain "flag" (index of a list in a dictionary). In our __init__.py test file we generate a dictionary with keys corresponding to different functions that have the branch coverage implemented along with lists of bools that correspond to each branch in that function. Then as all the tests are run we update the corresponding indexes of the flag lists thus clearly showing us which branches have been visited or not. A brief example of this is shown below:


```python
# __init__.py file where covering dict is created

# Here you add your function, initializing all the branches to False
covering = {}
# example: The function 'export' has 24 branches 
covering["export"] = [False for _ in range(24)]


# This is called at the end, and pretty-prints the branch coverage 
def count_covering():
    for func in covering:
        print(func + ":", end='\n\t')
        s = 0
        for i, e in enumerate(covering[func]):
            print(f"{i}: {e}", end="\n\t")
            s += (1 if e else 0)
        print(f"total coverage: {s / len(covering[func])}")

register(count_covering)
```
Example of how the flag statements can look:

```python

def export(x,y,z):

   if x < 10:
      covering["export"][0] = True
      # Function does something
   elif x > 10:
      covering["export"][1] = True
      # Function does something
   if y == 0:
      covering["export"][2] = True
      # Function does something

   # and so on for all branches of the function
```

Show a patch (or link to a branch) that shows the instrumented code to
gather coverage measurements.

These commits showcase how we implemented our coverage measurements

[Coverage commit #1](https://github.com/pdm-project/pdm/commit/0a16bc1edcac1a59e7979b07368982c0dbdf1413)

[Coverage commit #2]( https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/75a4bafed534a2b85da5fee6cefef88a91a6ebe6)

[Coverage commit #3]( https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/9f33899026dd9d96c2c9934ec52a80719614e9f0)

[Coverage commit #4](https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/7c66cb5c96906f9c4fe513559308ae5fc1463c33)

[Coverage commit #5]( https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/dcf317a41f40634b3288d4d590c5336ce1439946)

[Coverage commit #6 (bugfix)]( https://github.com/KTH-DD2480-Fundsoft/pdm-assignment-3/commit/0010671d72d293490057724084cc531785f16ac8)




The patch is probably too long to be copied here, so please add
the git command that is used to obtain the patch instead:

see links to commits above

What kinds of constructs does your tool support, and how accurate is
its output?
Our coverage tool works for most constructs but do not work with one line for loops and if statements that are embedded inside one another. An example of this construct that we don't support is:

```python
example = [j for j in range(10)]
```
Since we need to add our flags we need an extra line which is not possible for such constructs. If we've accurately implemented our lines that set the flags then our coverage tool is very accurate for the functions that include this feature. One problem that we encountered however was how some embedded for loops are difficult to rewrite into normal for loops with conditional statements which can potentially limit how well we can implement our flag conditions in our functions. 

### Evaluation

1. How detailed is your coverage measurement?
Our coverage measurement is very detailed for the functions that include our changes that allow us to set the flags of our functions. We are however limited to only checking the coverage for the functions that we've altered to work with our coverage tool. Thus we cannot generate coverage values for the entire library which severely limits our coverage scope. Our tool is able to take into account ternary operators and exceptions as we manually set the flag conditions. 

2. What are the limitations of your own tool?
We have to implement the checks for the different lines that set the flags (indexes of our list) manually which severely limits the amount of functions that we can check the branch coverage for. We also currently have to set the keys and values of the coverage dictionary manually as well. Thus we are very limited in fully implementing our tool for the entire library. A potential improvement to this would maybe be to integrate this with a library that measures complexity of the functions and automatically sets the different flag conditions and coverage dictionary.

3. Are the results of your tool consistent with existing coverage tools?
Our coverage tool is implemented for certain functions which makes it very difficult to compare with the existing coverage tool that was already integrated in the pdm repository. The existing coverage tool that we used checked the coverage of an entire module/python file which thus includes many classes and functions and doesn't allow us to compare our results directly. 

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

### What are your main take-aways from this project? What did you learn?
One thing we all realised is how difficult working in open source projects 
can be, as it takes a lot of time figuring out a code-base and getting used 
to other peoples code-style and patterns. We really realised during this 
assignment, working with `pdm`, how important documentation and comments 
are. `pdm` is lacking in these areas, and their onboarding does not cover 
all that we would like to know before we started working on the project.
For example, how the tests are structured with fixtures and how the different 
modules interact. We learnt how Githubs workflow, with forks, is designed. 

A lot of us got some good insight into testing -- the idea of coverage 
and that it is an actual measurement, that can be made quite easily with a 
tool such as coverage or the builtin coverage in pytest, was new to a lot of
us. We also got a good look on some practical examples of code coverage and 
complexity, by analysing control flow and counting branches of -- in some 
cases -- really complex functions.

### Is there something special you want to mention here?

We're happy with our choice of project, although we realised a bit into the 
assignment that some aspects of pdm where a bit unclear. As a result, we 
spent a lot of time just getting to know the code base -- more than we'd like.

