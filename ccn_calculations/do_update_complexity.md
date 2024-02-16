## Complexity of do_update@91-200@src/pdm/cli/commands/update.py

### Cyclomatic complexity number 
Using the formula explained [here](https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity) (which probably is the same one used in Lizard), I get the cyclomatic complexity number (CCN) to be 36. This is a bit dubious though since this method counts every boolean expression as adding 1 to the cyclomatic complexity number. Thus the snippet
```condition = A or B```
adds one to the CCN which is rather strange. Lizard appears to use the same method however since its calculation of do_update is also 36.

### Information about do_update
do_update is the function that is run to update the packages in `pyproject.toml`. Updating packages is a complicated task that requires much error handling which is one of the key reasons for the high CCN. The function is also rather long, about 100 lines, which contributes to its high CCN. Much complexity also comes from the specific way of calculating CCN. In my method (and Lizard's), the code snippet
```
reqs = [
    r
    for g, deps in all_dependencies.items()
    for r in deps.values()
    if locked_groups is None or g in locked_groups
]
``` 
adds 4 to the CCN. This is a whole lot but in some other methods, this wouldn't add anything to the CCN.


