# Ad-hoc code coverage `do_add`

## Quality
The coverage is using a simple list where the list index corresponds to the zero-indexed numbering of branches in the function.
So, `covering[0]` is true if branch `0` has been reached.

I used [this guide](https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity) to determine branches, and subsequently included 
list comprehensions and even regular boolean expressions.

## Limitations
The instrumentation will of course not funciton correctly if the code is changed, as the assignments `covering[x] = True` will need to be 
moved accordingly. 

## Not an automated tool
