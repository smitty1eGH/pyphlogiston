from dataclasses import dataclass

import pytest

from lib.pyphlogiston import RAO,data_import

#def test_RAO(rao):
#    print(rao.summary())


def test_import(rao,test_data):
    data_import(rao,test_data)
