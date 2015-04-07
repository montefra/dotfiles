#!/usr/bin/env python
# virtualenvwrapper
# This hook is sourced after a new virtualenv is activated.
# link pyqt 4, 5 and sip into the virtualenv

from __future__ import print_function

import glob
import os
import sys

# save the VIRTUAL_ENV path
virtual_env = sys.argv[1]

# get the site-packages directory
site_packages = glob.glob(os.path.join(virtual_env, "lib*", "python*",
                                       "site-packages"))[0]

has_pyqt4 = False
has_pyqt5 = False

# try to get pyqt 4. If it works symlink it
try:
    import PyQt4
    has_pyqt4 = True
    pyqt_dir = os.path.split(PyQt4.__file__)[0]
    pyqt_name = os.path.split(pyqt_dir)[1]
    os.symlink(pyqt_dir, os.path.join(site_packages, pyqt_name))
    print("PyQt4 symlinked")
except ImportError:
    print("no PyQt4 installed on the system")

# try to get pyqt 5. If it works symlink it
try:
    import PyQt5
    has_pyqt5 = True
    pyqt_dir = os.path.split(PyQt5.__file__)[0]
    pyqt_name = os.path.split(pyqt_dir)[1]
    os.symlink(pyqt_dir, os.path.join(site_packages, pyqt_name))
    print("PyQt5 symlinked")
except ImportError:
    print("no PyQt5 installed on the system")

# if pyqt is found link sip
if has_pyqt4 or has_pyqt5:
    import sip
    sip_so = sip.__file__
    sip_file = os.path.split(sip_so)[1]
    os.symlink(sip_so, os.path.join(site_packages, sip_file))
    sipdir = os.path.split(sip_so)[0]
    for pyfile in glob.glob(os.path.join(sipdir, "sip*py")):
        pyf = os.path.split(pyfile)[1]  # just the file name
        os.symlink(pyfile, os.path.join(site_packages, pyf))

    print("sip symlinked")

print('done')
