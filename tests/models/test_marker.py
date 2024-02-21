import pytest

from pdm.models.markers import get_marker
from pdm.models.markers import _build_pyspec_from_marker


@pytest.mark.parametrize(
    "original,marker,py_spec",
    [
        ("python_version > '3'", "", ">=3.1"),
        ("python_version > '3.8'", "", ">=3.9"),
        ("python_version != '3.8'", "", "!=3.8.*"),
        ("python_version == '3.7'", "", ">=3.7,<3.8"),
        ("python_version in '3.6 3.7'", "", ">=3.6,<3.8"),
        ("python_full_version >= '3.6.0'", "", ">=3.6"),
        ("python_full_version not in '3.8.3'", "", "!=3.8.3"),
        # mixed marker and python version
        ("python_version > '3.7' and os_name == 'nt'", 'os_name == "nt"', ">=3.8"),
        (
            "python_version > '3.7' or os_name == 'nt'",
            'python_version > "3.7" or os_name == "nt"',
            "",
        ),
    ],
)
def test_split_pyspec(original, marker, py_spec):
    m = get_marker(original)
    a, b = m.split_pyspec()
    assert marker == str(a)
    assert py_spec == str(b)



'''
Add 4 new tests to test_marker.py

The tests test that 
* _build_pyspec_from_marker of MultiMarker with unsupported marker type raises TypeError
* _build_pyspec_from_marker of MarkerUnion with unsupported marker type raises TypeError
* get_marker of an invalid marker string raises RequirementError
* get_marker of Marker instance returns a Marker with the same string representation

The tests enters branches of the functions _build_pyspec_from_marker and get_marker that 
were not covered previously. 

Old branch coverage: 82%
New branch coverage: 91%

'''


# new test 1
from dep_logic.markers import MultiMarker, MarkerUnion
def test_build_pyspec_from_marker_multi_marker():
    """
    Test that MultiMarker with unsupported marker type raises TypeError
    """
    m = get_marker("python_version > '3'")
    python_marker = m.inner.only("python_version, python_full_version", "python_full_version")
    multi_marker = MultiMarker(python_marker)

    with pytest.raises(TypeError) as exc_info:
        _build_pyspec_from_marker(multi_marker)

    assert "Unsupported marker type:" in str(exc_info.value)


# new test 2
def test_build_pyspec_from_marker_marker_union():
    """
    Test that MarkerUnion with unsupported marker type raises TypeError
    """
    m = get_marker("python_version > '3'")
    python_marker = m.inner.only("python_version, python_full_version", "python_full_version")
    marker_union = MarkerUnion(python_marker)

    with pytest.raises(TypeError) as exc_info:
        _build_pyspec_from_marker(marker_union)

    assert "Unsupported marker type:" in str(exc_info.value)


# New test 3
from pdm.exceptions import RequirementError
def test_get_marker_invalid_marker():
    """
    Test that get_marker of an invalid marker string raises RequirementError
    """
    invalid_marker = "invalid_marker_syntax"  # This marker is invalid
    with pytest.raises(RequirementError):
        get_marker(invalid_marker) # Expect RequirementError


# New test 4
from packaging.markers import Marker
def test_get_marker_marker_instance():
    """
    Test that get_marker of Marker instance returns a Marker with the same string representation
    """
    marker = Marker('python_version > "3.6"')
    result = get_marker(marker)
    # Assert that the result is the same Marker instance (using the string)
    assert str(result) == str(marker)