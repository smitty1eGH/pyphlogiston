from collections import OrderedDict
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
import json
import pprint
from uuid import uuid4 as uu

import pytest
import botocore.session
from botocore.loaders import Loader


from lib.dao import DAO

class APIType(Enum):
    '''These are the values that can appear in the DAO how table.
    '''
    IAMShape = 0
    IAMOp    = 1

@dataclass_json
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
    apitype   : APIType=APIType.IAMShape.name

@dataclass_json
@dataclass
class APIOp():
    uuid      : str = ''
    name      : str = ''
    http      : str = ''
    input     : str = ''
    output    : str = ''
    errors    : str = ''
    documentation : str = ''
    apitype   : APIType=APIType.IAMOp.name

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
    '''These ordered dicts are harder to work with.
         by the time we demote to regular dicts, life is easier
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

@pytest.mark.skip
def test_DAO_0():
    dao = DAO(APIType)

@pytest.mark.skip
def test_DAO_1(iam_enums):
    '''Do the Ops
    '''
    dao = DAO(APIType)
    for o in iam_enums[1]:
        op = toD(iam_enums[0]['operations'][o.name])
        op['uuid'] = str(uu())
        oq = APIOp(**{k:v for k,v in op.items()})

@pytest.mark.skip
def test_DAO_2(iam_enums):
    '''Ops to SQL
        print(getattr(oq,'input' ,None))
        print(getattr(oq,'output',None))
    '''
    dao = DAO(APIType)
    for o in iam_enums[1]:
        op = toD(iam_enums[0]['operations'][o.name])
        op['uuid'] = str(uu())
        oq = APIOp(**{k:v for k,v in op.items()})
        print(dao.dao_insert(oq))

def test_DAO_3(iam_enums):
    '''First we will enumerate the shapes, and then
        build up the ops.
    Ops to SQL
        print(getattr(oq,'input' ,None))
        print(getattr(oq,'output',None))
    '''
    dao = DAO(APIType)
    shapes={}
    types={'map','structure','list'}
    for o in iam_enums[2]:
        sh=iam_enums[0]['shapes'][o.name]
        if sh['type'] in types:
            try:
                op = toD(sh)
            except AttributeError as e:
                continue
            else:
                try:
                    op['uuid'] = str(uu())
                    op['name'] = o.name
                    shapes[o.name] = op['uuid']
                    oq = APIShape(**{k:v for k,v in op.items()})
                except KeyError as e:
                    print(e)

    for o in iam_enums[1]:
        op = toD(iam_enums[0]['operations'][o.name])
        op['uuid'] = str(uu())
        oq = APIOp(**{k:v for k,v in op.items()})
        print(dao.dao_insert(oq))
