import subprocess
import sys
import importlib
import re



def is_installed(package):
    try:
        #importlib.import_module(package.split('==')[0]) ### This doesn't check the version. Only package name
        importlib.import_module(
                re.sub(
                    "[^a-zA-Z]",
                    "", # removes any chars that are not a-z or A-Z sub. with nothing.
                    package
                    )
                )
                return True
    except:
        return False


def install(package):
    """ Requires that pip and python be in the users path """
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_depends():
    f = open('requirements.txt','r')
    for line in f:
        package = line
        if is_installed(package)==False: ## if false it will not run
            install(package)
        else:
            print('Installed')
            continue



install_depends()
