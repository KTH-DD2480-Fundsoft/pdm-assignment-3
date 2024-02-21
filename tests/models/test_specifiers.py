import pytest

from pdm.models.specifiers import PySpecSet
from pdm.models.versions import Version
from pdm.models.specifiers import _normalize_op_specifier
from pdm.exceptions import InvalidPyVersion


@pytest.mark.filterwarnings("ignore::FutureWarning")
@pytest.mark.parametrize(
    "original,normalized",
    [
        (">=3.6", ">=3.6"),
        ("<3.8", "<3.8"),
        ("~=2.7.0", ">=2.7,<2.8"),
        ("", ""),
        (">=3.6,<3.8", ">=3.6,<3.8"),
        (">3.6", ">=3.6.1"),
        ("<=3.7", "<3.7.1"),
        ("<3.3,!=3.4.*,!=3.5.*", "<3.3"),
        (">=3.6,!=3.4.*", ">=3.6"),
        (">=3.6,!=3.6.*", ">=3.7"),
        (">=3.6,<3.8,!=3.8.*", ">=3.6,<3.8"),
        (">=2.7,<3.2,!=3.0.*,!=3.1.*", ">=2.7,<3.0"),
        ("!=3.0.*,!=3.0.2", "!=3.0.*"),
        (">=3.4.*", ">=3.4"),
        (">3.4.*", ">=3.4"),
        ("<=3.4.*", "<3.4"),
        ("<3.4.*", "<3.4"),
        (">=3.0+g1234", ">=3.0"),
        ("<3.0+g1234", "<3.0"),
        ("<3.10.0a6", "<3.10.0a6"),
        ("<3.10.2a3", "<3.10.2a3"),
    ],
)
def test_normalize_pyspec(original, normalized):
    spec = PySpecSet(original)
    assert str(spec) == normalized


@pytest.mark.parametrize(
    "left,right,result",
    [
        (">=3.6", ">=3.0", ">=3.6"),
        (">=3.6", "<3.8", ">=3.6,<3.8"),
        ("", ">=3.6", ">=3.6"),
        (">=3.6", "<3.2", "impossible"),
        (">=2.7,!=3.0.*", "!=3.1.*", ">=2.7,!=3.0.*,!=3.1.*"),
        (">=3.11.0a2", "<3.11.0b", ">=3.11.0a2,<3.11.0b0"),
        ("<3.11.0a2", ">3.11.0b", "impossible"),
    ],
)
def test_pyspec_and_op(left, right, result):
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert str(left & right) == result


@pytest.mark.parametrize(
    "left,right,result",
    [
        (">=3.6", ">=3.0", ">=3.0"),
        ("", ">=3.6", ""),
        (">=3.6", "<3.7", ""),
        (">=3.6,<3.8", ">=3.4,<3.7", ">=3.4,<3.8"),
        ("~=2.7", ">=3.6", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*"),
        ("<2.7.15", ">=3.0", "!=2.7.15,!=2.7.16,!=2.7.17,!=2.7.18"),
        (">3.11.0a2", ">3.11.0b", ">=3.11.0a3"),
    ],
)
def test_pyspec_or_op(left, right, result):
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert str(left | right) == result


def test_impossible_pyspec():
    spec = PySpecSet(">=3.6,<3.4")
    a = PySpecSet(">=2.7")
    assert spec.is_impossible
    assert (spec & a).is_impossible
    assert spec | a == a
    spec_copy = spec.copy()
    assert spec_copy.is_impossible
    assert str(spec_copy) == "impossible"


@pytest.mark.filterwarnings("ignore::FutureWarning")
@pytest.mark.parametrize(
    "left,right",
    [
        ("~=2.7", ">=2.7"),
        (">=3.6", ""),
        (">=3.7", ">=3.6,<4.0"),
        (">=2.7,<3.0", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"),
        (">=3.6", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"),
        (
            ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
            ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
        ),
        (">=3.11.*", ">=3.11.0rc"),
    ],
)
def test_pyspec_is_subset_superset(left, right):
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert left.is_subset(right), f"{left}, {right}"
    assert right.is_superset(left), f"{left}, {right}"


@pytest.mark.parametrize(
    "left,right",
    [
        ("~=2.7", ">=2.6,<2.7.15"),
        (">=3.7", ">=3.6,<3.9"),
        (">=3.7,<3.6", "==2.7"),
        (">=3.0,!=3.4.*", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"),
        (">=3.11.0", "<3.11.0a"),
    ],
)
def test_pyspec_isnot_subset_superset(left, right):
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert not left.is_subset(right), f"{left}, {right}"
    assert not left.is_superset(right), f"{left}, {right}"

'''
The test requirements do not include versions outside of bounds [lower, upper], 
some normalization of operator specifiers, invalid operation specifiers, 
invalid PySpecSet parameters, tests for is_allow_all(), or tests for the 
__eq__ operator. 
'''

def test_pyspec_removal_non_valid_versions():
    '''
    Check that _merge_bounds_and_excludes removes versions outside of the bound
    [lower, upper].
    '''
    lower = Version("2.7.0")
    upper = Version("3.5.0")
    excludes = [Version("1.5.0"), Version("3.5.0"), Version("3.3.0"), Version("1.9.0"), 
                Version("2.7.0")]
    lower, upper, sorted_excludes = PySpecSet._merge_bounds_and_excludes(lower, upper, excludes)

    assert Version("1.5.0") not in sorted_excludes
    assert Version("1.9.0") not in sorted_excludes

@pytest.mark.parametrize(
        "op, version_str, expected_op, expected_version_str",
        [
            ("==", "3.2.*", "~=", "3.2.0"),
            (">", "2.9.*", ">=", "2.10.0"),
            ("<", "4.5.*", "<", "4.5.0"),
            ("<=", "2.3.*", "<", "2.3.0")
        ],
)
def test_normalize_op_specifier(op, version_str, expected_op, expected_version_str):
    '''
    Test normalization of operator specifiers. Here 
    == should transform to ~=,
    x.x.* should transform to x.x.0, 
    >x.0.* to >= x.1.0,
    <=x.0.* to <x.0.0.
    '''
    expected_version = Version(expected_version_str)
    op, version = _normalize_op_specifier(op, version_str)
    
    assert op == expected_op
    assert version == expected_version

def test_normalize_op_specifier_invalid_op():
    '''
    Using an invalid operation specifier should raise
    an InvalidPyVersion exception.
    '''
    op = "invalid_op"
    version_str = "3.2.*"
    with pytest.raises(InvalidPyVersion) as _:
        _normalize_op_specifier(op, version_str)

def test_analyze_specifiers_invalid_pyversion():
    '''
    Creating a PySpecSet with an invalid python version
    should raise and InvalidPyVersion exception.
    '''
    with pytest.raises(InvalidPyVersion) as _:
        PySpecSet("~~~=11.2.2*")

def test_is_allow_all():
    spec_set = PySpecSet("*")
    spec_set._lower_bound = Version("5.4.3")
    spec_set._upper_bound = Version("2.2.0")
    assert spec_set.is_allow_all == False

@pytest.mark.parametrize(
        "first, second, expected_bool",
        [
            (PySpecSet("*"), PySpecSet(""), True),
            (PySpecSet(">=2.3.2"), set(), False),
            (PySpecSet("*"), 2, False),
        ],
)
def test_pyspec_set_equality_operator(first, second, expected_bool):
    '''
    Parameterized test for the PySpecSet equality operator. Equality 
    should only be true if the two objects have the same lower and upper
    bound and the same exclude tuple.
    '''
    assert (first == second) == expected_bool
