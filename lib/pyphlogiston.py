from os import chdir, getcwd
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
    5. checkout data/repo/repo.fossil to data/stage

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

def _run_command(fossil, args):
    '''
    '''
    print([fossil] + args)
    out = run([fossil] + args, capture_output=True)
    try:
        assert out.returncode == 0
    except AssertionError as e:
        print(f'_run_command error for {fossil} {args}\n\tError => {out}')
    return out

def add_files(proj_path, fossil, args):
    '''
    '''
    _args=['add', f'{proj_path}']
    for a in args:
        _args.append(a)
    return _run_command(fossil, _args)

def commit_files(proj_path, fossil, tag, message):
    args=['commit', '--no-prompt' ,'--nosign' ,'--tag' ,tag ,'-m' ,message ,f'{proj_path}/data/stage/*']
    return _run_command(fossil,args)

def add_and_commit(proj_path, fossil, tag, message):
    '''Temporarily shift to proj_path to do the add.
       TODO: go with a chdir context manager if this is more needful
    '''
    old=getcwd()
    chdir(proj_path)
    out0=add_files(proj_path, fossil,[])
    out1=commit_files(proj_path, fossil, tag, message)
    chdir(old)
    return out0,out1
