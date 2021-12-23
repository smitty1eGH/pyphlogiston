from os import chdir, getcwd
from pathlib import Path
from shutil import copy2 as copy
from subprocess import run

from dao import DAO

class RAO:
    """The Repository Access Object

    This is the interface for CRUD operations against the repo.
    """

    def __init__(self, config, categories):
        """
        PROJ_PATH is the root of the client project
        FOSSIL    is the path the the fossil executable

        Build:
        PROJ_PATH/data/pyphlogiston.sqlite
                      /stage/
                      /repo/phlogiston.fossil

        1. set up           data/
        2. initialize       data/pyphlogiston.sqlite
        3. set up           data/stage/
        4. set up           data/repo
        5. initialize       data/repo/repo.fossil
        6. commit stage/ to data/repo/repo.fossil
        """
        # TMP_PATH would be the install directory
        # 1, 2, 3:
        b = Path(str(proj_path) + "data")
        b.mkdir()
        for d in ["/stage", "/repo"]:
            c = Path(str(b) + d)
            c.mkdir()
        self._dao = DAO(categories)

        # 4.
        r = Path(f"{str(proj_path)}data/repo")
        chdir(str(r))
        init = [fossil, "init", "phologiston.fossil"]
        out = run(init, capture_output=True)
        assert out.returncode == 0

        # 5.
        s = Path(f"{str(proj_path)}data/stage")
        co = [fossil, "open", f"{str(r)}/phologiston.fossil", "--workdir", str(s)]
        out = run(co, capture_output=True)
        assert out.returncode == 0

    def _run_command(fossil, args):
        """Wrapper for the commands to run against the fossil repo"""
        print([fossil] + args)
        out = run([fossil] + args, capture_output=True)
        try:
            assert out.returncode == 0
        except AssertionError as e:
            print(f"_run_command error for {fossil} {args}\n\tError => {out}")
        return out

    def add_files(proj_path, fossil, args):
        """ """
        _args = ["add", f"{proj_path}"]
        for a in args:
            _args.append(a)
        return _run_command(fossil, _args)

    def commit_files(proj_path, fossil, tag, message):
        args = [
            "commit",
            "--no-prompt",
            "--nosign",
            "--tag",
            tag,
            "-m",
            message,
            f"{proj_path}",
        ]
        return _run_command(fossil, args)

    def add_and_commit(proj_path, fossil, tag, message):
        """Temporarily shift to proj_path to do the add.
        TODO: go with a chdir context manager if this is more needful
        """
        old = getcwd()
        chdir(proj_path)
        out0 = add_files(proj_path, fossil, [])
        out1 = commit_files(proj_path, fossil, tag, message)
        chdir(old)
        return out0, out1
