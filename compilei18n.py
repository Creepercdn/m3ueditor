"""
Usage:
compilei18n.py <lrelease path> <translate files path> <options to lrelease(DO NOT SET -ts)>
"""

import subprocess
import sys
import os
import locale

lrelease = 'lrelease' # lrelease path
workspace = './i18n/'
options = []
files = []
concoding = "utf-8"
concoding = locale.getpreferredencoding()

if __name__=="__main__":
    lrelease = sys.argv[1]
    workspace = sys.argv[2]
    options = sys.argv[3:]

    files = os.listdir(workspace)
    for i in range(len(files)):
        files[i] = os.path.abspath(os.path.join(workspace,files[i]))
    files = filter(os.path.isfile, files)
    files = filter(lambda x: os.path.splitext(x)[-1]=='.ts', files)

    for i in files:
        subprocess.run(f"{lrelease} {' '.join(options)} {os.path.abspath(os.path.join(workspace, i))}")
