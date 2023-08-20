from os import chdir
from pathlib import Path
from subprocess import run

PROJ_NAME = "pyphlogiston"
PROJ_ROOT = "/home/smitty/proj"

# from install_profile import PROJ_NAME, PROJ_ROOT, get_config

# In get_config() a project root path and name are taken,
#   and, the file system/repo are prepared, and a
# 

def setup_fossil(tmp_path, fossil, proj_name):
    """
    1. set up  data
    2.         data/stage
    3.         data/repo
    4.         data/repo/repo.fossil
    """
    # 1, 2, 3:
    p = str(tmp_path)
    b = Path(f"{p}/data")
    b.mkdir()
    stage = Path(f"{str(b)}/stage")
    stage.mkdir()
    repo = Path(f"{str(b)}/repo")
    repo.mkdir()

    # 4.
    chdir(str(repo))
    out = run([fossil, "init", f"{proj_name}.fossil"], capture_output=True)
    assert out.returncode == 0


def get_config(proj_name=PROJ_NAME, proj_root=PROJ_ROOT):
    '''Calculate, validate, and return a working config,
    creating directories as needful
    '''
    conf = { "FOSSIL"     : "/usr/bin/fossil"
           , "FOSSIL_REPO_NAME" : f"{proj_name}.fossil"
           , "PROJ_PATH"  : f"{proj_root}/{proj_name}/{proj_name}/"
           , "PROJ_DATA"  : f"data/{proj_name}.fossil"
           , "PROJ_DEFS"  :  "data/defaults.pickle"
           , "PROJ_IMGS"  :  "data/images"
           , "SQLITE_FILE": f"{proj_name}.sqlite"
           }
    if not Path(conf['FOSSIL']).exists():
        return {'Error':'no fossil'}
    if not Path(conf['PROJ_PATH']).exists():
        Path(conf['PROJ_PATH']).mkdir(parents=True)
        setup_fossil(conf['PROJ_PATH'], conf['FOSSIL'], proj_name)
    return conf
