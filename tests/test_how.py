import json
import sqlite3

import pytest

def jobj(uuid ,apitype,data):
    return '{"uuid":"%s","apitype":%s,"data":%s}' % (uuid ,apitype,data)

def rolled_jobj(conn,uuid):
    AS_STRING=0
    sql=f"""SELECT jobj(uuid,apitype,data -> '$.data')
            FROM   Vwhat
            WHERE  uuid='{uuid}';
         """
    return [r for r in conn.execute(sql)][AS_STRING]

def rolled_jchi(conn,uuid):
    sql=f"""SELECT jobj(cuuid,ctype,'""')
            FROM   how
            WHERE  puuid='{uuid}';
         """
    return '[%s]' % ','.join([str(r)[2:-3] for r in conn.execute(sql)])

@pytest.fixture
def uuid():
    return '7fa6090d-2757-4387-877e-4db394a4594b'

@pytest.fixture
def db():
    return 'asdf.sqlite'

@pytest.fixture
def conn(db):
    c=sqlite3.connect(db)
    c.create_function("jobj", 3, jobj)
    return c

def test_sql(conn,uuid):
    #We render the interpolation into the second marker a no-op here.
    obj0='{"content":%s, "children":%s}' % (rolled_jobj(conn,uuid)[0],'%s')
    obj1=json.loads(obj0 % rolled_jchi(conn,uuid))
    print(json.dumps(obj1,indent=2))
