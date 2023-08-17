from subprocess import run

import pytest

from etc.install_profile import PROJ_NAME, PROJ_ROOT, get_config

@pytest.fixture
def status():
    '''Return the command to get fossil status
    '''
    return ["systemctl", "--user", "status", "-l", "fossil.service"]

@pytest.fixture
def fossil():
    return "/usr/bin/fossil"

@pytest.fixture
def proj_name():
    return "phlogiston"

@pytest.fixture
def repo_name(proj_name):
    return f"{proj_name}.fossil"


@pytest.fixture
def config(proj_name,repo_name,tmp_path):
    return get_config(proj_name, tmp_path)

@pytest.fixture
def data_path():
    return "/home/smitty/proj/pyphlogiston/pyphlogiston/data/"

@pytest.fixture
def setup_fossil(tmp_path, fossil):
    """
    1. set up  data
    2.         data/checkout
    3.         data/repo
    4.         data/repo/repo.fossil
    5.checkout data/repo/repo.fossil to data/stage

    return the staging path
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
    out = run([fossil, "init", "phologiston.fossil"], capture_output=True)
    assert out.returncode == 0

    # 5.
    out = run(
        [fossil, "open", f"{str(repo)}/phologiston.fossil", "--workdir", str(stage)],
        capture_output=True,
    )
    assert out.returncode == 0

    return str(stage)
