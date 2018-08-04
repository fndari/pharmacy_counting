from pharmacy_counting.util import *
from pharmacy_counting.data import DrugSummary
import pytest


def test_defaultdictkeyasarg_str():
    d = DefaultDictKeyAsArg(str)

    assert d['something'] == 'something'
    assert d[0] == '0'


def test_defaultdictkeyasarg_int():
    d = DefaultDictKeyAsArg(int)
    assert d[0] == 0, 'works as expected with trivial input'
    assert d[1235] == 1235, 'check that the argument is passed as expected'
    with pytest.raises(ValueError):
        assert d['something']


class ObjWithArg:

    def __init__(self, arg):
        self.arg = arg


def test_defaultdictkeyasarg_obj():
    d = DefaultDictKeyAsArg(ObjWithArg)
    d['some_key'].arg = 'some_key'


def test_skip_line_msg(capfd):
    log_skipped_stdout(123, 'Error message')

    out, err = capfd.readouterr()
    assert out == 'Skipping line 123: Error message\n'
