import pytest
from pdm.models.specifiers import PySpecSet
from pdm.models.versions import Version

class TestPySpecSet:
    def test_method1(self):
        version_1 = Version("3.11")
        version_2 = Version("3.20")
        lower, upper, sorted_excludes = PySpecSet._merge_bounds_and_excludes(version_1, version_2, [])
        print("lower", lower)
        print("upper", upper)
        print("sorted_excludes", sorted_excludes)

    def test_method2(self):
        assert False == False