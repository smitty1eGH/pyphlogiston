from os import chdir
from pathlib import Path
from shutil import copy2 as copy
from subprocess import run

import pytest


@pytest.fixture
def fossil():
    return "/usr/bin/fossil"


@pytest.fixture
def repo_name():
    return "phlogiston.fossil"


@pytest.fixture
def data_path():
    return "/home/smitty/proj/pyphlogiston/pyphlogiston/data/"


@pytest.fixture
def setup_script(tmp_path, fossil):
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


@pytest.fixture
def test_repo(fossil, tmp_path, repo_name):
    out = run([fossil, "init", f"{tmp_path}/{repo_name}"], capture_output=True)
    assert out.returncode == 0
    return f"{tmp_path}/{repo_name}"


@pytest.fixture
def add_files0(data_path):
    p = Path(data_path)
    return [str(f) for f in p.glob("**/*")]


def test_fossil_version(fossil):
    out = run([fossil, "version"], capture_output=True)
    assert out.returncode == 0


def test_repo_info(fossil, test_repo, setup_script):
    ASDF = (
        "/tmp/pytest-of-smitty/pytest-current/test_repo_infocurrent/phlogiston.fossil"
    )
    chdir(setup_script)
    out = run([fossil, "add", f"{setup_script}/*"], capture_output=True)
    assert out.returncode == 0
    out = run([fossil, "info", ASDF], capture_output=True)
    assert out.returncode == 0


def test_add(setup_script, fossil, add_files0):
    """
    6. stick files in data/checkout
    7. do the rest of the fossil thing
    """
    chdir(setup_script)
    for a in add_files0:
        copy(a, setup_script)

    out = run([fossil, "add", f"{setup_script}/*"], capture_output=True)
    assert out.returncode == 0
