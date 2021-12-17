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
from lib.botofier import toD, toJ


class APIType(Enum):
    """These are the values that can appear in the DAO how table."""

    IAMShape = 0
    IAMOp = 1


@dataclass_json
@dataclass
class APIShape:
    uuid: str
    name: str
    box: str = ""
    enum: str = ""
    error: str = ""
    exception: str = ""
    key: str = ""
    min: str = ""
    max: str = ""
    member: str = ""
    members: str = ""
    pattern: str = ""
    required: str = ""
    sensitive: str = ""
    type: str = ""
    value: str = ""
    documentation: str = ""
    apitype: APIType = APIType.IAMShape.name

    def mems(self):
        out=[]
        if self.member != '':
            out.append(self.member['shape'])
        if self.members !='':
            out.append(self.members)
        return ','.join(out)

@dataclass_json
@dataclass
class APIOp:
    uuid: str = ""
    name: str = ""
    http: str = ""
    input: str = ""
    output: str = ""
    errors: str = ""
    documentation: str = ""
    apitype: APIType = APIType.IAMOp.name

@pytest.fixture
def iam_service():
    session = botocore.session.get_session()
    return session.create_client("iam", region_name="us-east-1")


@pytest.fixture
def iam_file():
    l = Loader()
    # print(l.list_available_services('service-2'))
    return l.load_service_model("iam", "service-2")


@pytest.fixture
def iam_enums(iam_file):
    IAMOps = Enum("IAMOps", " ".join([x for x in iam_file["operations"].keys()]))
    IAMShapes = Enum("IAMShapes", " ".join([x for x in iam_file["shapes"].keys()]))
    return iam_file, IAMOps, IAMShapes


@pytest.mark.skip
def test_loader(iam_file):
    '''RETURNS:
       version
       metadata
       operations
       shapes
       documentation
    '''
    for k in iam_file.keys():
        print(k)


@pytest.mark.skip
def test_IAMOps(iam_enums):
    """These ordered dicts are harder to work with.
    by the time we demote to regular dicts, life is easier
    """
    for o in iam_enums[1]:
        od = iam_enums[0]["operations"][o.name]
        n = od["name"]
        try:
            i = od["input"]["shape"]
            print(f"input: {n}\t{i}")
        except KeyError as e:
            pass
        try:
            o = od["output"]["shape"]
            print(f"ouput: {n}\t{o}")
        except KeyError as e:
            pass


@pytest.mark.skip
def test_DAO_0():
    dao = DAO(APIType)


@pytest.mark.skip
def test_DAO_1(iam_enums):
    """Do the Ops
    """
    dao = DAO(APIType)
    for o in iam_enums[1]:
        op = toD(iam_enums[0]["operations"][o.name])
        op["uuid"] = str(uu())
        oq = APIOp(**{k: v for k, v in op.items()})


@pytest.mark.skip
def test_DAO_2(iam_enums):
    """Ops to SQL
    print(getattr(oq,'input' ,None))
    print(getattr(oq,'output',None))
    """
    dao = DAO(APIType)
    for o in iam_enums[1]:
        op = toD(iam_enums[0]["operations"][o.name])
        op["uuid"] = str(uu())
        oq = APIOp(**{k: v for k, v in op.items()})
        print(dao.dao_insert(oq))


def test_DAO_3(iam_enums):
    """First we will enumerate the shapes, and then
        build up the ops.
    Ops to SQL
        print(getattr(oq,'input' ,None))
        print(getattr(oq,'output',None))

    operations entry dict keys:
      types = {"map", "structure", "list"}

    {'type', 'error', 'documentation', 'member', 'key'
    , 'min', 'value', 'members', 'max', 'exception'}
    """
    all_your_ops    = {}
    all_your_shapes = {}
    all_your_uuids  = {} # Generate UUIDs for any names
                         #   encountered, irrespective of whether
                         #   they have yet been encountered in the data.
    def do_uuid(name):
        if name not in all_your_uuids:
            all_your_uuids[name] = str(uu())

    dao   = DAO(APIType)
    types = {"map","list","structure"}
    for o in iam_enums[2]:
        sh = iam_enums[0]["shapes"][o.name]
        if sh["type"] in types:
            op = toD(sh)
            match op['type']:

                case 'map':
                    do_uuid(op[ "key"    ]["shape"])
                    do_uuid(op[ "value"  ]["shape"])
                    print(f'{all_your_uuids[""]}')

                case 'structure':
                    do_uuid(o.name)
                    name = o.name
                    op["name"] = name
                    op["uuid"] = all_your_uuids[name]
                    all_your_shapes[name]=APIShape(**{k: v for k, v in op.items()})

                    deps=[]
                    for m in op["members"]:
                        n =op["members"][m]
                        do_uuid( m )
                        n["name"] = m
                        n["uuid"] = all_your_uuids[m]
                        deps.append(all_your_uuids[m])
                        all_your_shapes[m]=APIShape(*n)
                    all_your_shapes[name].members=','.join(deps)

                case 'list':
                    do_uuid(op[ "member" ]["shape"])
                    name = op[  "member" ]["shape"]
                    op["name"] = name
                    op["uuid"] = all_your_uuids[name]
                    all_your_shapes[name]=APIShape(**{k: v for k, v in op.items()})

                case 'str':
                    do_uuid(o.name)


    #for k,v in all_your_shapes.items():
    #    print(f'{k}\n\t{v.mems}')

    #print(f'{all_your_uuids=}')
    #print(len(all_your_uuids.keys()))

    #for o in iam_enums[1]:
    #    op = toD(iam_enums[0]["operations"][o.name])
    #    op["uuid"] = str(uu())
    #    all_your_ops[o.name] = APIOp(**{k: v for k, v in op.items()})
        #print(dao.dao_insert(oq))
