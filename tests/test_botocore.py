from dataclasses import dataclass
from enum import Enum

import pytest
import botocore.session
from botocore.loaders import Loader

class APIType(Enum):
    IAMShape = 0
    IAMOp    = 1


@dataclass
class APIShape():
    uuid      : str
    name      : str
    key       : str = ''
    type      : str = ''
    required  : str = ''
    min       : str = ''
    max       : str = ''
    enum      : str = ''
    pattern   : str = ''
    value     : str = ''
    exception : str = ''
    members   : str = ''
    box       : str = ''
    error     : str = ''
    member    : str = ''
    sensitive : str = ''
    documentation : str = ''
    apitype   : APIType=APIType.IAMShape.value


@dataclass
class APIOp():
    uuid      : str = ''
    name      : str = ''
    http      : str = ''
    input     : str = ''
    output    : str = ''
    errors    : str = ''
    documentation : str = ''
    apitype   : APIType=APIType.IAMOp.value


@pytest.fixture
def iam_service():
    session = botocore.session.get_session()
    return session.create_client('iam',region_name='us-east-1')


@pytest.fixture
def iam_file():
    l= Loader()
    #print(l.list_available_services('service-2'))
    return l.load_service_model('iam','service-2')

@pytest.fixture
def iam_enums(iam_file):
    IAMOps=Enum('IAMOps',' '.join([x for x in iam_file['operations'].keys()]))
    IAMShapes=Enum('IAMShapes',' '.join([x for x in iam_file['shapes'].keys()]))
    return iam_file,IAMOps,IAMShapes

def test_loader(iam_file):
    for k in iam_file.keys():
        print(k)

def test_IAMOps(iam_enums):
    '''
    '''
    for o in iam_enums[1]:
        od=iam_enums[0]['operations'][o.name]
        n=od['name']
        try:
            i=od['input']['shape']
        except KeyError as e:
            i=None
        try:
            o=od['output']['shape']
        except KeyError as e:
            o=None
        #print(f'{n}\t{i}\t{o}')

    types={'map','structure', 'list'}
    #n=sh['name']
    for o in iam_enums[2]:
        sh=iam_enums[0]['shapes'][o.name]
        if sh['type'] in types:
            try:
                #Need to add a comprehension on "members" to determine
                #  relevant shapes
                print(f'{o.name}\t{sh["members"]}')
            except KeyError as e:
                pass


