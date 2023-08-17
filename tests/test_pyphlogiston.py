import pytest

from lib.pyphlogiston import RAO
from w5lib import WType


def test_RAO(config):
    rao=RAO(config,WType)
