# Refactoring plan - `clean_metadata`

This is the current state of the function:

```python
def clean_metadata(metadata: Dict[str, Any]) -> None:
    author = {}
    if "author" in metadata:
        author["name"] = metadata.pop("author")
    if "author_email" in metadata:
        author["email"] = metadata.pop("author_email")
    if author:
        metadata["authors"] = [author]
    maintainer = {}
    if "maintainer" in metadata:
        maintainer["name"] = metadata.pop("maintainer")
    if "maintainer_email" in metadata:
        maintainer["email"] = metadata.pop("maintainer_email")
    if maintainer:
        metadata["maintainers"] = [maintainer]

    urls = {}
    if "url" in metadata:
        urls["Homepage"] = metadata.pop("url")
    if "download_url" in metadata:
        urls["Downloads"] = metadata.pop("download_url")
    if "project_urls" in metadata:
        urls.update(metadata.pop("project_urls"))
    if urls:
        metadata["urls"] = urls

    if "" in metadata.get("package_dir", {}):
        metadata["package_dir"] = metadata["package_dir"][""]

    if "keywords" in metadata:
        keywords = metadata["keywords"]
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]
        metadata["keywords"] = keywords

    if "entry_points" in metadata and isinstance(metadata["entry_points"], dict):
        entry_points = {}
        for entry_point, definitions in metadata["entry_points"].items():
            if isinstance(definitions, str):
                definitions = [definitions]
            definitions = dict(sorted(d.replace(" ", "").split("=", 1) for d in definitions))

            entry_points[entry_point] = definitions
        if entry_points:
            metadata["entry_points"] = dict(sorted(entry_points.items()))
```

**Is the high complexity you identified really necessary?**

It is clear that the complexity is unnecessary since it consists of several blocks of  `if`-statements which do something to some data structure given some conditions. All of these could essentially be broken down into smaller units. Furthermore, the parts where the function transforms the `metadata` when it contains the keys `keywords` and `entry_points` can also be refactored into their own units.

**Is it possible to split up the code (in the five complex functions you have identified) into smaller units to reduce complexity? If so, how would you go about this?**

We can identify six blocks of code which would be suitable to refactor into separate functions. These blocks of code are the following:

1. Handle author-related information
2. Handle maintainer-related information
3. Handle URL-related
4. Handle package directory
5. Handle keywords
6. Handle entry points

Thus, we can create a function for each of these blocks of code:

```python
def handle_person_info(metadata: Dict[str, Any], role: str) -> Dict[str, Any]:
    """
    Extracts and returns information for a person (author or maintainer) from metadata.
    """
    person_info = {}
    if f"{role}" in metadata:
        person_info["name"] = metadata.pop(f"{role}")
    if f"{role}_email" in metadata:
        person_info["email"] = metadata.pop(f"{role}_email")
    return person_info

def handle_urls(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts URLs information from metadata and returns a dictionary of URLs.
    """
    urls = {}
    if "url" in metadata:
        urls["Homepage"] = metadata.pop("url")
    if "download_url" in metadata:
        urls["Downloads"] = metadata.pop("download_url")
    if "project_urls" in metadata:
        urls.update(metadata.pop("project_urls"))
    return urls

def adjust_package_dir(metadata: Dict[str, Any]) -> None:
    """
    Adjusts the package directory in metadata if necessary.
    """
    if "" in metadata.get("package_dir", {}):
        metadata["package_dir"] = metadata["package_dir"][""]

def handle_keywords(metadata: Dict[str, Any]) -> None:
    """
    Processes the keywords in metadata to ensure they are in a list format.
    """
    if "keywords" in metadata:
        keywords = metadata["keywords"]
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]
        metadata["keywords"] = keywords

def handle_process_entry_points(metadata: Dict[str, Any]) -> None:
    """
    Processes the entry points in metadata, organizing and sorting them.
    """
    if "entry_points" in metadata and isinstance(metadata["entry_points"], dict):
        entry_points = {}
        for entry_point, definitions in metadata["entry_points"].items():
            if isinstance(definitions, str):
                definitions = [definitions]
            definitions = dict(sorted(d.replace(" ", "").split("=", 1) for d in definitions))

            entry_points[entry_point] = definitions
        if entry_points:
            metadata["entry_points"] = dict(sorted(entry_points.items()))
```

One thing to note is that the two first identified block of codes are handled by the same function `handle_person_info`, which modularily handles the same type of transormation being made on `author` information and `maintainer` information. With these, we can put them together into a `clean_metadata` function with reduced complexity:

```python
def clean_metadata(metadata: Dict[str, Any]) -> None:
    author_info = handle_person_info(metadata, "author")
    if author_info:
        metadata["authors"] = [author_info]

    maintainer_info = handle_person_info(metadata, "maintainer")
    if maintainer_info:
        metadata["maintainers"] = [maintainer_info]

    urls = handle_urls(metadata)
    if urls:
        metadata["urls"] = urls

    adjust_package_dir(metadata)
    handle_keywords(metadata)
    handle_process_entry_points(metadata)
```

By doing this, the function `clean_metadata` gets a CCN of 4!