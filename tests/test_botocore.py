from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
import json
import pprint

import pytest
import botocore.session
from botocore.loaders import Loader


from lib.dao import DAO

class APIType(Enum):
    '''These are the values that can appear in the DAO how table.
    '''
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

def toD(od):
    '''Return a botocore OrderedDict as a regular dict.
    '''
    out={}
    for k,v in od.items():
        if isinstance(v,OrderedDict):
            out[k]=toD(v)
        elif isinstance(v,list):
            tmp={}
            for l in v:
                m=toD(l)
                for n,o in m.items():
                    if n in tmp:
                        tmp[n].append(o)
                    else:
                        tmp[n]=[o]
            out[k]=tmp
        else:
            out[k]=v
    return out

def toJ(od):
    return json.loads(json.dumps(toD(od)))

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
            print(f'input: {n}\t{i}')
        except KeyError as e:
            pass
        try:
            o=od['output']['shape']
            print(f'ouput: {n}\t{o}')
        except KeyError as e:
            pass

   # types={'map','structure', 'list'}
   # #n=sh['name']
   # for o in iam_enums[2]:
   #     sh=iam_enums[0]['shapes'][o.name]
   #     if sh['type'] in types:
   #         try:
   #             #Need to add a comprehension on "members" to determine
   #             #  relevant shapes
   #             print(f'{o.name}\t{sh["members"]}')
   #         except KeyError as e:
   #             pass

def test_DAO_0():
    dao = DAO(APIType)

def test_DAO_1(iam_enums):
    dao = DAO(APIType)
    for o in iam_enums[1]:
        print(iam_enums[0]['operations'][o.name])
