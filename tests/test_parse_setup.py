import pytest

import pdm.models.in_process.parse_setup as ps

'''
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
'''


@pytest.mark.parametrize(
    "input_metadata, expected_output", [
    ({"author": "John Doe"}, {"authors": [{"name": "John Doe"}]})
])
def test_clean_metadata_with_author(input_metadata, expected_output):
    '''
    Tests that `clean_metadata` correctly transforms an `input_metadata`
    with a key-value pair:
        `"author" : <X>`
    so that the key-value pair is transformed into a key-value pair:
        `"authors" : [{"name": <X>, ...}]`
    '''
    ps.clean_metadata(input_metadata)
    assert input_metadata == expected_output

@pytest.mark.parametrize(
    "input_metadata, expected_output", [
    ({"author_email": "john.doe@example.com"}, {"authors": [{"email": "john.doe@example.com"}]})
])
def test_clean_metadata_with_author_email(input_metadata, expected_output):
    '''
    Tests that `clean_metadata` correctly transforms an `input_metadata`
    with a key-value pair:
        `"author_email" : <X>`
    so that the key-value pair is transformed into a key-value pair:
        `"authors" : [{"email": <X>, ...}]`
    '''
    ps.clean_metadata(input_metadata)
    assert input_metadata == expected_output

@pytest.mark.parametrize(
    "input_metadata, expected_output", [
    ({"maintainer": "Jane Doe"}, {"maintainers": [{"name": "Jane Doe"}]})
])
def test_clean_metadata_with_maintainer(input_metadata, expected_output):
    '''
    Tests that `clean_metadata` correctly transforms an `input_metadata`
    with a key-value pair:
        `"maintainer" : <X>`
    so that the key-value pair is transformed into a key-value pair:
        `"maintainers" : [{"name": <X>, ...}]`
    '''
    ps.clean_metadata(input_metadata)
    assert input_metadata == expected_output

@pytest.mark.parametrize(
    "input_metadata, expected_output", [
    ({"maintainer_email": "jane.doe@example.com"}, {"maintainers": [{"email": "jane.doe@example.com"}]})
])
def test_clean_metadata_with_maintainer_email(input_metadata, expected_output):
    '''
    Tests that `clean_metadata` correctly transforms an `input_metadata`
    with a key-value pair:
        `"maintainer_email" : <X>`
    so that the key-value pair is transformed into a key-value pair:
        `"maintainers" : [{"email": <X>, ...}]`
    '''
    ps.clean_metadata(input_metadata)
    assert input_metadata == expected_output

