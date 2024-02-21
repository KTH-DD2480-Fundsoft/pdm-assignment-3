# Refactoring the function `_parse_setup_cfg` from src/pdm/models/in_process/parse_setup.pysynchronizers.py

## Objective
The function `_parse_setup_cfg` currently has a CCN of 29. The objective is to refactor the function into smaller units to reduce complexity with at least 35%. The target CCN is a value less than or equal to 18. 

## Idea 
The function `_parse_setup_cfg` is 82 lines long and looks like this:

```python
def _parse_setup_cfg(path: str) -> Dict[str, Any]:
    import configparser

    setup_cfg = configparser.ConfigParser()
    setup_cfg.read(path, encoding="utf-8")

    result: Dict[str, Any] = {}
    if not setup_cfg.has_section("metadata"):
        return result

    metadata = setup_cfg["metadata"]

    if "name" in metadata:
        result["name"] = metadata["name"]

    if "description" in metadata:
        result["description"] = metadata["description"]

    if "license" in metadata:
        result["license"] = metadata["license"]

    if "author" in metadata:
        result["author"] = metadata["author"]

    if "author_email" in metadata:
        result["author_email"] = metadata["author_email"]

    if "maintainer" in metadata:
        result["maintainer"] = metadata["maintainer"]

    if "maintainer_email" in metadata:
        result["maintainer_email"] = metadata["maintainer_email"]

    if "keywords" in metadata:
        keywords = metadata["keywords"].strip().splitlines()
        result["keywords"] = keywords if len(keywords) > 1 else keywords[0]

    if "classifiers" in metadata:
        result["classifiers"] = metadata["classifiers"].strip().splitlines()

    if "url" in metadata:
        result["url"] = metadata["url"]

    if "download_url" in metadata:
        result["download_url"] = metadata["download_url"]

    if "project_urls" in metadata:
        result["project_urls"] = dict(
            [u.strip() for u in url.split("=", 1)] for url in metadata["project_urls"].strip().splitlines()
        )

    if "long_description" in metadata:
        long_description = metadata["long_description"].strip()
        if long_description.startswith("file:"):
            result["readme"] = long_description[5:].strip()

    if setup_cfg.has_section("options"):
        options = setup_cfg["options"]

        if "python_requires" in options:
            result["python_requires"] = options["python_requires"]

        if "install_requires" in options:
            result["install_requires"] = options["install_requires"].strip().splitlines()

        if "package_dir" in options:
            result["package_dir"] = dict(
                [p.strip() for p in d.split("=", 1)] for d in options["package_dir"].strip().splitlines()
            )

    if setup_cfg.has_section("options.extras_require"):
        result["extras_require"] = {
            feature: dependencies.strip().splitlines()
            for feature, dependencies in setup_cfg["options.extras_require"].items()
        }

    if setup_cfg.has_section("options.entry_points"):
        result["entry_points"] = {
            entry_point: definitions.strip().splitlines()
            for entry_point, definitions in setup_cfg["options.entry_points"].items()
        }

    return result
```

The function consists mainly of if blocks without elif or else statements. The idea is to split the nested if-blocks into separate functions. If this is not eough to reduce the CCN to 18, the function will be split up further by placing the if-blocks containing for-loops into functions. If this is not enough we will try gathering if-blocks with similar purposes into functions too. 

## Identifying submodules
We begin by refactoring lines 57-60 and 62-74 into functions.

### lines 57-60
```python
if "long_description" in metadata:
    long_description = metadata["long_description"].strip()
    if long_description.startswith("file:"):
        result["readme"] = long_description[5:].strip()
```
This block changes the state of long_description and result. Move this to a function we need to pass the relevant variables as input to the function and retrieve them in a tuple as output. 

#### suggested change: 
```python
def update_long_description_and_result(long_description: str, result: dict[str, Any], metadata: SectionProxy) -> (str, dict[str, Any]):
    if "long_description" in metadata:
        long_description = metadata["long_description"].strip()
        if long_description.startswith("file:"):
            result["readme"] = long_description[5:].strip()
    return (long_description, result)
```

### lines 62-74
```python
    if setup_cfg.has_section("options"):
        options = setup_cfg["options"]

        if "python_requires" in options:
            result["python_requires"] = options["python_requires"]

        if "install_requires" in options:
            result["install_requires"] = options["install_requires"].strip().splitlines()

        if "package_dir" in options:
            result["package_dir"] = dict(
                [p.strip() for p in d.split("=", 1)] for d in options["package_dir"].strip().splitlines()
            )
```

#### suggested change: 
```python
def update_options_and_result(options: SectionProxy, result: dict[str, Any], setup_cfg: ConfigParser) -> (SectionProxy, dict[str, Any]):
    if setup_cfg.has_section("options"):
        options = setup_cfg["options"]

        if "python_requires" in options:
            result["python_requires"] = options["python_requires"]

        if "install_requires" in options:
            result["install_requires"] = options["install_requires"].strip().splitlines()

        if "package_dir" in options:
            result["package_dir"] = dict(
                [p.strip() for p in d.split("=", 1)] for d in options["package_dir"].strip().splitlines()
            )
    return(options, result)
```


## Further refactoring

### lines 76-86
```python
    if setup_cfg.has_section("options.extras_require"):
        result["extras_require"] = {
            feature: dependencies.strip().splitlines()
            for feature, dependencies in setup_cfg["options.extras_require"].items()
        }

    if setup_cfg.has_section("options.entry_points"):
        result["entry_points"] = {
            entry_point: definitions.strip().splitlines()
            for entry_point, definitions in setup_cfg["options.entry_points"].items()
        }
```

#### suggested change: 
```python
def update_result(result: dict[str, Any], setup_cfg: ConfigParser) -> dict[str, Any]:
    if setup_cfg.has_section("options.extras_require"):
        result["extras_require"] = {
            feature: dependencies.strip().splitlines()
            for feature, dependencies in setup_cfg["options.extras_require"].items()
        }

    if setup_cfg.has_section("options.entry_points"):
        result["entry_points"] = {
            entry_point: definitions.strip().splitlines()
            for entry_point, definitions in setup_cfg["options.entry_points"].items()
        }
    return result
```

## Results and refactoring evaluation
to-do