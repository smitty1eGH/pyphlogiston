from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json
import typing
import sqlite3
from uuid import uuid4 as uu

from .w5lib import wtypes

DEFAULT = "__default__"

# Data Access Object wraps the sqlite file that is the present tense
#   state of the application.

def jobj(uuid,apitype,data):
    '''Called from within SQL to format a row as a JSON object.
    initialized at the end of DAO.__init__()
    '''
    return '{"uuid":"%s","apitype":%s,"data":%s}' % (uuid ,apitype,data)

@dataclass_json
@dataclass
class DefVal:
    """DefVal(uuid=,apitype=)
    Every category has a default value automatically generated.
    """

    uuid: str = ""
    apitype: str = ""
    name: str = DEFAULT
    data: str = DEFAULT

class DAO:
    """Data Access Object for SQLite database that is:
      - an adjacency list for a set of category tables,
      - based upon the enumeration provided to __init__
    Category data for those tables are required to have at least
      - `name` and
      - `type` fields
    Note that there is no UPDATE functionality; the system versions
      data using fossil.
    The class supports actively inserting data if given a connection via
      the *_do flavors, or returning statements via *_sql flavors.
    Set dry_run=True to see what select, insert, or ins_how SQL would have
      been executed.
    """

    TBLPREF = "T"  # Prefix database object names to
    VIEWPRF = "V"  #    obviate reserved word collisions
    PARENT = 0
    CHILD = 1

    def __init__(self, categories, db_path=":memory:"):
        """Initialize a list of tables with the names of the categories
        that retained in the SQLite adjacency list.
        Instantiate db, load default data
        """

        def gen_defaults(self):
            """Populate the following.

            - a list of inserts of default values, and
            - a global default object cache
            """
            for x in self.tables:
                self.cache[x] = uu()  # default uuid for the table
                self.cache[f"{x}_lru"] = None  # last recently used
                yield self.insert(DefVal(uuid=str(self.cache[x]), apitype=wtypes[x]), dry_run=True)

        self.categories = categories
        self.cache = {}
        self.tables = [x.name for x in categories]
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)

        """Build the T{base} and 'how' DDL for SQLite
           Add on views that pull name/type fields out of data
        """
        self.schema = [
            f"""CREATE TABLE {self.TBLPREF}{t}(uuid TEXT,data TEXT);"""
            for t in self.tables
        ]
        self.schema.append(
            """CREATE TABLE how(puuid TEXT   , ptype INTEGER, cuuid TEXT
                               ,ctype INTEGER, data  TEXT);"""
        )
        for t in self.tables:
            self.schema.append(
                f"""CREATE VIEW {self.VIEWPRF}{t} AS
                    SELECT uuid
                         , json_extract(data,'$.name'   ) AS name
                         , json_extract(data,'$.apitype') AS apitype
                         , data
                    FROM  {self.TBLPREF}{t};
                 """
            )
        for q in gen_defaults(self):
            self.schema.append(q)

        with self._conn as c:
            try:
                c.create_function("jobj", 3, self.jobj)
                c.executescript("".join(self.schema))
            except Exception as e:
                print(e)
            finally:
                c.commit()


    @property
    def conn(self):
        """Return database connection."""
        return self._conn

    def summary(self):
        """Summary report."""
        SQL0 = ["SELECT 'how',COUNT(*) FROM how"]
        SQL1 = f"SELECT '%s', COUNT(*) FROM {self.TBLPREF}%s"
        for x in self.tables:
            SQL0.append(SQL1 % (x, x))
        SQL2 = " UNION ".join(SQL0)
        cur = self._conn.cursor()
        res = cur.execute(SQL2)
        return [str(r) for r in res]

    def select(self, category, name, dry_run=False):
        """Return data from query."""
        if dry_run:
            FINDME = "%s"
            sql0 = f"SELECT a.uuid FROM {DAO.VIEWPRF}%s AS a WHERE a.name={FINDME};"
            sql1 = sql0 % category.name
            return self._conn.execute(sql1, name)
        else:
            FINDME = "?"
            sql = f"SELECT a.uuid FROM {DAO.VIEWPRF}%s AS a WHERE a.name={FINDME};"
            return sql % (category.name, name)

    def insert(self, data, dry_run=False):
        if dry_run:
            INSERTER = "'%s','%s'"
            sql = f"INSERT INTO {DAO.TBLPREF}%s(uuid,data)  VALUES ({INSERTER});"
            return sql % (wtypes[data.apitype], data.uuid, data.to_json())
        else:
            INSERTER = "?,?"
            sql0 = f"INSERT INTO {DAO.TBLPREF}%s(uuid,data)  VALUES ({INSERTER});"
            sql1 = sql0 % (wtypes[data.apitype])
            self._conn.execute(sql1, (str(data.uuid), data.to_json()))
            self._conn.commit()

    def ins_how(self, parent, child, data=None, dry_run=False):
        use_data = data or ""
        argtuple = (str(parent.uuid), parent.apitype, str(child.uuid), child.apitype, use_data)
        if dry_run:
            INS_HOW = "'%s',%s,'%s',%s,'%s'"
            sql = f"INSERT INTO how(puuid,ptype,cuuid,ctype,data) VALUES ({INS_HOW});"
            return sql % argtuple
        else:
            INS_HOW = "?,?,?,?,?"
            sql = f"INSERT INTO how(puuid,ptype,cuuid,ctype,data) VALUES ({INS_HOW});"
            try:
                if parent.name == "UpdateUserRequest":
                    print(f"{parent=}\n{child=}")
                self._conn.execute(sql, argtuple)
                self._conn.commit()
            except AttributeError as e:
                print(e)

    def rolled_jobj(self,uuid):
        AS_STRING=0
        sql=f"""SELECT jobj(uuid,apitype,data -> '$.data')
                FROM   Vwhat
                WHERE  uuid='{uuid}';
             """
        return [r for r in self._conn.execute(sql)][AS_STRING][0]

    def rolled_jchi(self,uuid):
        sql=f"""SELECT jobj(cuuid,ctype,'""')
                FROM   how
                WHERE  puuid='{uuid}';
             """
        return '[%s]' % ','.join([str(r)[2:-3] for r in self._conn.execute(sql)])

    def add_object_to_fossil(self,uuid):
        '''When an object is added, we
        1. insert the data into the table
        2. insert the how data into the table
        3. generate a JSON document for committing to the repository
        '''
        #We render the interpolation into the second marker a no-op here.
        obj0='{"content":%s, "children":%s}' % (self.rolled_jobj(uuid),'%s')
        obj1=json.loads(obj0 % rolled_jchi(uuid))
        return json.dumps(obj1,indent=2)
