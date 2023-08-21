from os import chdir
from pathlib import Path
from subprocess import run

PROJ_NAME = "pyphlogiston"
PROJ_ROOT = "/home/smitty/proj"

# from install_profile import PROJ_NAME, PROJ_ROOT, get_config

# In get_config() a project root path and name are taken,
#   and, the file system/repo are prepared, and a
# 

def get_config(proj_name=PROJ_NAME, proj_root=PROJ_ROOT):
    '''Calculate, validate, and return a working config,
    creating directories as needful
    '''
    REPO=f"{proj_name}.fossil"
    conf = { "FOSSIL"     : "/usr/bin/fossil"
           , "FOSSIL_REPO_NAME" : REPO
           , "PROJ_PATH"  : f"{proj_root}/"
           , "PROJ_REPO"  : f"data/{REPO}"           # Fossil repo
           , "PROJ_DEFS"  :  "data/defaults.pickle"
           , "PROJ_IMGS"  :  "data/images"
           , "PROJ_STAGE" :  "data/stage"
           , "SQLITE_FILE": f"data/{proj_name}.sqlite"
           }
    if not Path(conf['FOSSIL']).exists():
        return {'Error':'no fossil'}
    Path(conf['PROJ_PATH']+'data').mkdir(parents=True)
    out = run([conf['FOSSIL'], "init", f"{conf['PROJ_PATH']}{conf['PROJ_REPO']}"], capture_output=True)
    assert out.returncode == 0
    return conf
