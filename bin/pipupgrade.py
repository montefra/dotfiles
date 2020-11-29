#!/usr/bin/env pthon3
"""
 upgrade packages in .local and in the virtualenvs installed via
 ``virtualenvwrapper``

 usage: pipupgrade

 Copyright (C) 2020 Francesco Montesano <franz.bergesund@gmail.com>

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import functools
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess as sp
from typing import Iterable, List

import pytest


logger = logging.getLogger(__name__)


def get_subprocess_stdout(cmd: List[str]) -> str:
    p = sp.run(cmd, stdout=sp.PIPE, encoding="UTF-8")
    p.check_returncode()

    return p.stdout


def get_packages_to_update(pip: Path) -> Iterable[str]:
    logger.info("Search for packages to update")
    options = "list -l -o --format freeze"

    stdout = get_subprocess_stdout([pip, ] + options.split())

    for line in stdout.splitlines():
        package_name = line.split("==")[0]
        yield package_name


def update_local(pip: Path):
    packages = list(filter(functools.partial(is_package_local, pip),
                           get_packages_to_update(pip)))

    if packages:
        logger.info("%s: updating packages %s", pip.name, ", ".join(packages))
        options = "install --use-feature=2020-resolver -U --user"
        stdout = get_subprocess_stdout([pip, ] + options.split() + packages)

        logger.info("Packages updated")
        logger.debug(stdout)
    else:
        logger.warning("no packages to update with %s", pip.name)


def update_venv(pip: Path, env_name: str):
    packages = list(get_packages_to_update(pip))

    if packages:
        logger.info("%s: updating packages %s", env_name, ", ".join(packages))
        options = "install --use-feature=2020-resolver -U"
        stdout = get_subprocess_stdout([pip, ] + options.split() + packages)

        logger.info("Packages updated")
        logger.debug(stdout)
    else:
        logger.warning("no packages to update in %s", env_name)


def is_package_local(pip: Path, package: str) -> bool:
    pattern = r"\nLocation: .*?local/lib.*?\n"
    match = re.search(pattern, get_subprocess_stdout([pip, "show", package]))

    if match is None:
        logger.warning("To upgrade %s first re-install it using --user",
                       package)
        return False
    return True


def _setup_logger():
    fmt = '%(asctime)s - %(levelname)s - %(message)s'

    logfile = Path.home() / ".pip" / "pip_upgrade.log"
    file_handler = logging.FileHandler(logfile, mode="w", encoding="UTF-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(fmt))

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def update_pyenv_environments():
    pyenv_root = os.environ.get("PYENV_ROOT")
    if pyenv_root and Path(pyenv_root).is_dir():
        pyenv_root = Path(pyenv_root)

        pyenv_cmd = "pyenv versions --skip-aliases --bare"
        versions = get_subprocess_stdout(pyenv_cmd.split())

        for version in versions.splitlines():
            logger.info("====================")

            pip = pyenv_root / "versions" / version / "bin" / "pip"
            update_venv(pip, version)
    else:
        logger.info("Pyenv not installed, nothing to do")


def main():
    _setup_logger()

    if os.environ.get("VIRTUAL_ENV"):
        msg = ("The script does not work properly when launched from a"
               " virtual environment")
        logger.error(msg)
        raise EnvironmentError(msg)

    pip3 = Path(shutil.which("pip3"))
    update_local(pip3)

    update_pyenv_environments()


if __name__ == "__main__":
    main()


@pytest.fixture
def subprocess_run_mock(monkeypatch):
    def _run_mock(mock_stdout: str):
        process = sp.CompletedProcess("mock command".split(), 0,
                                      stdout=mock_stdout)

        monkeypatch.setattr(sp, "run", lambda *_, **__: process)

    return _run_mock


def test_get_packages_to_upgrade(subprocess_run_mock):
    mock_packages = "package1==1.2.3\npackage2==1.3.4\npackage3==1.2.4"
    subprocess_run_mock(mock_packages)

    pip = Path("pip")

    packages = list(get_packages_to_update(pip))

    assert packages == ["package1", "package2", "package3"]


@pytest.mark.parametrize("location, is_local",
                         [("/home/user/.local/lib/python3.6/site-packages",
                           True),
                          ("/usr/lib/python/site-packages", False)
                          ])
def test_is_package_local(subprocess_run_mock, location, is_local):
    pip_show = f"""
Name: ansible
Version: 2.10.3
Summary: Radically simple IT automation
Home-page: https://ansible.com/
Author: Ansible, Inc.
Author-email: info@ansible.com
License: GPLv3+
Location: {location}
Requires: ansible-base
Required-by:
"""
    subprocess_run_mock(pip_show)

    assert is_package_local(Path("pip"), "mock_package") == is_local
