import typing
import sqlite3
from uuid import uuid4 as uu


class DAO():
    """Data Access Object for SQLite database that's an adjacency
      list for a set of category tables generated based
      upon the enumeration provided to __init__
    Category data for those tables are required to have at least
      - `name` and
      - `type` fields
    Note that there is no UPDATE functionality; the system versions
      data using fossil.
    The class supports actively inserting data if given a connection via
      the *_do flavors, or returning statements via *_sql flavors.
    """

    DEFAULT = "__default__"
    TBLPREF = "T"  # Prefix database object names to
    VIEWPRF = "V"  #    obviate reserved word collisions
    PARENT = 0
    CHILD = 1
    JSONTEMP = """json('{"name":"%s","type":%s,"payload":"%s"}')"""

    def __init__(self, categories, db_path=":memory:"):
        """Initialize a list of tables with the names of the categories
          that retained in the SQLite adjacency list.
        Instantiate db, load default data
        """
        self.categories = categories
        self.cache = {}
        self.tables = [x for x in categories.__members__]
        self.db_path = db_path

        """Build the T{base} and how DDL for SQLite
           Add on views that pull name/type fields out of data
        """
        self.schema = [
            f"CREATE TABLE {self.TBLPREF}{t}(uuid TEXT,data TEXT);" for t in self.tables
        ]
        self.schema.append(
            "CREATE TABLE how(puuid TEXT,ptype INTEGER,cuuid TEXT,ctype INTEGER,data TEXT);"
        )
        for t in self.tables:
            self.schema.append(
                f"CREATE VIEW {self.VIEWPRF}{t} AS SELECT uuid, json_extract(data,'$.name') AS name, json_extract(data,'$.type') AS type, data FROM {self.TBLPREF}{t};"
            )

        self.defs = self._defaults()
        self._conn = sqlite3.connect(self.db_path)
        cursor = self._conn.cursor()
        cursor.executescript("".join(self.schema))
        cursor.executescript("".join(self.defs))

    def _defaults(self):
        """Populate the following:
        - a list of inserts of default values, and
        - a global default object cache
        """
        out = []
        for x in self.tables:
            self.cache[x] = uu()  # default uuid for the table
            self.cache[f"{x}_lru"] = None  # last recently used
            out.append(
                self.INSERTER
                % (
                    x,
                    f"'{self.cache[x]}'",
                    self.JSONTEMP
                    % (self.DEFAULT, self.categories[x].value, self.DEFAULT),
                )
            )
        return out

    def conn(self):
        return self._conn

    def _select(self,s_or_q=True):
        if s_or_q:
            FINDME='%s'
        else:
            FINDME='?'
        return f"SELECT a.uuid FROM {VIEWPRF}%s AS a WHERE a.name={FINDME};"

    def select_sql(self, category, name):
        sql=self._select()
        return sql % (category.name, name)

    def select_do(self, conn, category, name):
        sql0=self._select(False)
        sql1=sql0 % category.name
        return conn.execute(sql1, name)

    INSERTER = f"INSERT INTO {TBLPREF}%s(uuid,data)  VALUES ('%s','%s');"
    INS_HOW  = ("INSERT INTO how(puuid,ptype,cuuid,ctype,data) VALUES ((%s),%s,(%s),%s,%s);")
    def insert_sql(self, data):
        return DAO.INSERTER % (data.apitype, data.uuid, data.to_json())

    def insert_do(self, conn, data):
        return DAO.INSERTER % (data.apitype, data.uuid, data.to_json())

    def ins_how_sql(self, parent, child, data=None):
        return DAO.INS_HOW & (
            parent.puuid,
            parent.ptype.value,
            child.cuuid,
            child.ctype.value,
            data,
        )

    def ins_how_do(self, conn, parent, child, data=None):
        return DAO.INS_HOW & (
            parent.puuid,
            parent.ptype.value,
            child.cuuid,
            child.ctype.value,
            data,
        )
