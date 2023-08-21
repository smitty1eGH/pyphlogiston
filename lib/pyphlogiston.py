from dataclasses import dataclass
from itertools   import tee, filterfalse
import json
from os          import chdir, getcwd
from pathlib     import Path
import sqlite3
from subprocess  import run
from uuid        import uuid4 as uuid

from lib.dao import DAO, DefVal
from lib.w5lib import DEFAULT, WType, wtypes

# The idea is that the Repository Access Object
#   wraps a SQLite file and associated Fossil
#   repository.
# Client code will instantiate the RAO and use the CRUD
#   methods provided, and get versioning for free.
# All data are immutable in the system.
#   UPDATEs do not really happen; the latest version with
#   a given UUID is the 'update'. DELETEs do not really
#   happen, either. Content set to __DELETED__ for a UUID
#   will be ignored. So, really, it's all CREATE and SELECT

# Usage:
#  1. Instantiate the config
#  2. Instantiate the RAO
#  3. Invoke the DAO functions that are boosted by the RAO


class RAO:
    """The Repository Access Object.

    This is the interface for CRUD operations against the repo.
    Objects shall have been written to data/stage whenever
      there is a change to the state of an object, and
      then all of the objects to add are stored in fossil
      via add_and_commit()

    TODO:
    - Add some .tar capability for the repo
    - Might also put it somewhere else that can be
      easily snapshotted
    """

    def __init__(self, config, categories=None):
        """Configure the structure.
        """
        self.config = config
        self.base = Path(f"{self.config['PROJ_PATH']}")
        self.repo = Path(f"{self.config['PROJ_PATH']}{self.config['PROJ_REPO']}")
        self.stage = Path(f"{self.config['PROJ_PATH']}{self.config['PROJ_STAGE']}")
        out = self._run_command(["open", str(self.repo), "--workdir", str(self.stage)])
        if categories:
            self._DAO = DAO(categories, f"{self.config['PROJ_PATH']}{self.config['SQLITE_FILE']}")

    def create_object(self, the_object):
        """Write an object to pyphlogiston.

        the_object is a JSON document that knows:
        - its UUID
        - its apitype
        - its name
        - other properties as desired
        """
        with open(f"{self.config.proj_path}/data/stage/{the_object.uuid}", "w") as f:
            f.write(json.dumps(the_object))
        self.add_and_commit()

    def _run_command(self, args):
        """Wrap commands to run against the fossil repo."""
        out = run([self.config['FOSSIL'], *args], capture_output=True)
        try:
            assert out.returncode == 0
        except AssertionError as e:
            print(f"_run_command error for {self.config['FOSSIL']} {args}\n\tError => {out.stdout}")
        return out

    def add_files(self, args):
        """Add files to repo."""
        args = ["add", f"{self.config.proj_path}"]
        for a in args:
            args.append(a)
        return self._run_command(self.config.fossil, args)

    def commit_files(self, tag, message):
        """Run the fossil commit command."""
        args = [
            "commit",
            "--no-prompt",
            "--nosign",
            "--tag",
            tag,
            "-m",
            message,
            f"{self.config.proj_path}",
        ]
        return self._run_command(args)

    def add_and_commit(self, tag, message):
        """Temporarily shift to proj_path to do the add.

        TODO: go with a chdir context manager if this is more needful
        """
        old = getcwd()
        chdir(self.config.proj_path)
        out0 = self.add_files()
        assert out0 == 0
        out1 = self.commit_files(
            self.config.proj_path, self.config.fossil, tag, message
        )
        assert out1 == 0
        chdir(old)
        return out0, out1

    def summary(self):
        '''Return the summary from the DAO
        '''
        return self._DAO.summary()


def data_import(rao,insertable_data,maybe_dry_run=False):
    '''1. Partition the keys in the content
       2. Do regular table inserts
       3. Do the 'how' inserts
       4. Use the uuid_cache to write out the resulting stage
            document for each object.
    '''
    def partition(iterable):
        JOIN_TABLE_FLAG='2'
        NOT_JOIN_TABLE=-1
        regular=lambda x:x.find(JOIN_TABLE_FLAG)==NOT_JOIN_TABLE
        t1, t2 = tee(iterable)
        return filterfalse(regular, t1), filter(regular, t2)

    # 1.
    uuid_cache={}
    d=insertable_data['content']
    join_tables, regular_tables=partition(d.keys())

    # 2.
    for i in regular_tables:
        for e in d[i]:
            f=DefVal(uuid   =e.get('uuid',uuid())
                    ,apitype=wtypes[i]
                    ,name   =e.get('name',DEFAULT)
                    ,data   =str(e) )
            uuid_cache[f.name]=f
            sql=rao._DAO.insert(f, dry_run=True)

    # 3.
    for i in join_tables:
        for e in d[i]:
            sql=rao._DAO.ins_how( uuid_cache[e[0]]
                                , uuid_cache[e[1]]
                                , data=''
                                , dry_run=True   )

    # 4.
    c2 = sqlite3.connect('./asdf.sqlite')
    conn = rao._DAO.conn
    conn.backup(c2)
    #for dv in uuid_cache.Values():
    #    with open(f'{str(self.stage)}{f.uuid}','w') as stage:
    #        stage.write(f.to_json())
