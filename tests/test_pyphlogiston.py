from dataclasses import dataclass
from itertools   import tee, filterfalse
from uuid        import uuid4 as uuid

import pytest

from lib.dao import DefVal
from lib.pyphlogiston import RAO
from lib.w5lib import DEFAULT, WType, wtypes

uuid_cache={}


def test_RAO(rao):
    print(rao.summary())


