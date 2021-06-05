# TODO pip package pgn to pngs
# TODO automatically generate .exe with github actions (nouveau repo)
# TODO select subset of image
# include resources
# reset and create app before pyinstaller
# set colors for non macos dists
#  https://pypi.org/project/appdirs/
# problem default python version and tcl version?
# https://github.com/pyinstaller/pyinstaller/issues/3820 > manuelf23

# default installation macos python
# laurent@Laurents-MacBook-Pro ~ % python

# WARNING: Python 2.7 is not recommended.
# This version is included in macOS for compatibility with legacy software.
# Future versions of macOS will not include Python 2.7.
# Instead, it is recommended that you transition to using 'python3' from within Terminal.

# Python 2.7.16 (default, Jun  5 2020, 22:59:21)
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc- on darwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import tkinter as tk
# >>> print(tk.Tcl().eval('info patchlevel'))
# 8.5.9

####################

# default installation macos python3
# laurent@Laurents-MacBook-Pro ~ % python3
# Python 3.8.3 (default, Jul  8 2020, 14:27:55)
# [Clang 11.0.3 (clang-1103.0.32.62)] on darwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import tkinter as tk
# >>> print(tk.Tcl().eval('info patchlevel'))
# 8.5.9

####################

# conda python3
# (label_chess) laurent@Laurents-MacBook-Pro label_chess % python
# Python 3.9.4 (default, Apr  9 2021, 09:32:38)
# [Clang 10.0.0 ] :: Anaconda, Inc. on darwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import tkinter as tk
# >>> print(tk.Tcl().eval('info patchlevel'))
# 8.6.10

# https://github.com/pyinstaller/pyinstaller/issues/5109 <- reritom

#####
# file access from bundled app different from not bundled
# need to see logs to know the error <-
pyinstaller label_chess/start_app.py \
    - -onefile \
    - -name label_chess \
    - -add-data = "resources/pieces/*:./resources/pieces"

python label_chess/start_app.py - -no_start - -reset_db

pyinstaller  \
    - -onefile label_chess/start_app.py \
    - w \
    - -icon = resources/pieces/wp.png \
    - -name label_chess \
    - -add-data = "resources/pieces/*:./resources/pieces" \
    - -add-data = "database/*:./database" \
    - -add-data = "db.sqlite:."
