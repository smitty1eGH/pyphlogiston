from os import chdir
from pathlib import Path
from shutil import copy2 as copy
from subprocess import run

def setup_script(proj_path, fossil):
    '''
    PROJ_PATH is the root of the client project
    FOSSIL    is the path the the fossil executable

    Build:
    PROJ_PATH/data
                  /stage
                  /repo/phlogiston.fossil

    1. set up a data directory
    2. set up a data/checkout directory
    3. set up a data/repo directory
    4. initialize data/repo/repo.fossil
    5. checkout data/repo/repo.fossil to data/checkout

    return the staging path
    '''
    #TMP_PATH would be the install directory
    # 1, 2, 3:
    b = Path(str(proj_path) + 'data')
    b.mkdir()
    for d in ['stage','repo']:
        c = Path(str(b) + d)
        c.mkdir()

    # 4.
    r = Path(f'{str(proj_path)}/data/repo' )
    r.mkdir(parents=True)
    chdir(str(r))
    init = [fossil,'init', 'phologiston.fossil']
    out = run(init, capture_output=True)
    assert out.returncode == 0

    # 5.
    s = Path(f'{str(proj_path)}/data/stage' )
    co =  [fossil,'open', f'{str(r)}/phologiston.fossil', '--workdir', str(s)]
    out = run(co, capture_output=True)
    assert out.returncode == 0

def add_files(proj_path, fossil):
    '''
    '''
    f = []
    f.append(fossil)
    f.append('add')
    f.append(f'{proj_path}/data/stage/*')
    out = run(f, capture_output=True)
    assert out.returncode == 0
