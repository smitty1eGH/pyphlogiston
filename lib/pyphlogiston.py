from dataclasses import dataclass
import json
from os import chdir, getcwd
from pathlib import Path
from subprocess import run

from dao import DAO

#Usage:
#  1. Instantiate the config
#  2. Instantiate the RAO
#  3. Invoke write_object() to populate



def write_object(config, rao, the_object):
    """Write an object to pyphlogiston.

    1. the_object is a JSON document that knows:
    - its UUID
    - its apitype
    - its name
    - other properties as desired
    2. write it to config.proj_path/data/stage
    3. invoke rao.add_and_commit()
    """

    with open(f"{config.proj_path}/data/stage/{the_object.uuid}", "w") as f:
        f.write(json.dumps(the_object))
    rao.add_and_commit()


@dataclass
class RAOConfig:
    """RAO configuration items to set."""

    fossil: str  # path to fossil binary
    proj_path: str  # top of the storage tree


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

        PROJ_PATH is the root of the client project
        FOSSIL    is the path the the fossil executable

        Build:
        PROJ_PATH/data/pyphlogiston.sqlite      # current state
                      /stage/                   # files with UUID names
                      /repo/phlogiston.fossil   # past states

        1. set up           data/
        2. initialize       data/pyphlogiston.sqlite
        3. set up           data/stage/
        4. set up           data/repo
        5. initialize       data/repo/repo.fossil
        6. commit stage/ to data/repo/repo.fossil
        """
        self.config = config

        # TMP_PATH would be the install directory
        # 1, 2, 3:
        self.base = Path(f"{str(self.config.proj_path)}/data")
        self.base.mkdir()
        self.stage = Path(f"{str(self.base)}/stage")
        self.stage.mkdir()
        self.repo = Path(f"{str(self.base)}/repo")
        self.repo.mkdir()

        # 4.
        chdir(str(self.repo))
        out = self._run_command(self, ["init", "phologiston.fossil"])

        # 5.
        out = self._run_command(self, ["open", f"{str(self.repo)}/phologiston.fossil", "--workdir", str(self.stage)])

        # 6.
        if categories:
            self.DAO = DAO(categories,f'{self.base}/pyphlogiston.sqlite')


    def _run_command(self, args):
        """Wrap commands to run against the fossil repo."""
        out = run([self.config.fossil] + args, capture_output=True)
        try:
            assert out.returncode == 0
        except AssertionError as e:
            print(f"_run_command error for {self.config.fossil} {args}\n\tError => {e}")
        return out

    def add_files(self, args):
        """Add files to repo."""
        args = ["add", f"{self.config.proj_path}"]
        for a in args:
            args.append(a)
        return self._run_command(self.config.fossil, args)

    def commit_files(self, tag, message):
        """Run the fossile commit command."""
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
        out0 = self.add_files(self.config.proj_path, self.config.fossil, [])
        assert out0 == 0
        out1 = self.commit_files(
            self.config.proj_path, self.config.fossil, tag, message
        )
        assert out1 == 0
        chdir(old)
        return out0, out1
