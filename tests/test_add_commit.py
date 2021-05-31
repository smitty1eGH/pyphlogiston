from os import chdir
from pathlib import Path
from shutil import copy2 as copy
from subprocess import run

import pytest

@pytest.fixture
def fossil():
    return '/home/osboxes/src/fossil-snapshot-20210429/fossil'


@pytest.fixture
def repo_path():
    return '/home/osboxes/proj/pyphlogiston/pyphlogiston/repo'

@pytest.fixture
def repo_name():
    return 'phlogiston.fossil'

@pytest.fixture
def data_path():
    return '/home/osboxes/proj/pyphlogiston/pyphlogiston/data'

@pytest.fixture
def setup_script(tmp_path, fossil, repo_path, repo_name, data_path):
    '''
    1. set up a data directory
    2. set up a data/checkout directory
    3. set up a data/repo directory
    4. initialize data/repo/repo.fossil
    5. checkout data/repo/repo.fossil to data/checkout

    return the staging path
    '''
    #TMP_PATH would be the install directory
    # 1, 2, 3:
    b = Path(str(tmp_path) + 'data')
    b.mkdir()
    for d in ['stage','repo']:
        c = Path(str(b) + d)
        c.mkdir()

    # 4.
    r = Path(str(tmp_path) + '//data//repo' )
    print(f'{r=}')
    r.mkdir(parents=True)
    chdir(str(r))
    init = [fossil,'init', 'phologiston.fossil']
    out = run(init, capture_output=True)
    assert out.returncode == 0

    # 5.
    s = Path(str(tmp_path) + '//data//stage' )
    print(f'{s=}')
    co =  [fossil,'open', f'{str(r)}/phologiston.fossil', '--workdir', str(s)]
    out = run(co, capture_output=True)
    assert out.returncode == 0

    return s




@pytest.fixture
def test_repo(fossil,tmp_path,repo_name):
    f = []
    f.append(fossil)
    test_path = f'{tmp_path}/{repo_name}'
    f.append('init')
    f.append(test_path)
    #print(f'{" ".join([f for f in fossil])}')
    out = run(f, capture_output=True)
    assert out.returncode == 0
    return test_path

@pytest.fixture
def add_files0(data_path):
    p = Path(data_path)
    return [str(f) for f in p.glob('./*')]

def test_fossil_version(fossil):
    f = []
    f.append(fossil)
    f.append('version')
    out = run(f, capture_output=True)
    assert out.returncode == 0

def test_repo_info(fossil,test_repo):
    f = []
    f.append(fossil)
    f.append('info')
    f.append(test_repo)
    #fossil.append('verbose')
    out = run(f, capture_output=True)
    assert out.returncode == 0
    #print()
    #print(out.stdout.decode('utf-8'))

def test_add(setup_script, fossil, add_files0):
    '''
    6. stick files in data/checkout
    7. do the rest of the fossil thing
    '''
    chdir(setup_script)
    for a in add_files0:
        copy(a, setup_script)

    f = []
    f.append(fossil)
    f.append('add')
    f.append(f'{setup_script}/*')
    out = run(f, capture_output=True)
    assert out.returncode == 0
    #print()
    #print(out.stdout.decode('utf-8'))
