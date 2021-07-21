# Args
## $1 path to the site-packages directory where the dependencies of this repo are installed.
## $2 version suffix to append to the file name.
# Examples
## Anaconda env, python 3.9 and version 0.0.1
### bash pyinstaller.sh ~/anaconda3/envs/<env-name>/lib/python3.9/site-packages 0.0.1
## virtualenv, python 3.7 and version 1.0.1-dev
### bash pyinstaller.sh <env-name>/lib/python3.7/site-packages 1.0.1-dev

# reset sqlite database
python3 start_app.py --reset_db --no_start

# remove .exe build artefacts
rm -r dist
rm -r build
rm label_chess-*.spec


# create app
pyinstaller  start_app.py \
    --onefile \
    --name label_chess-$2 \
    --icon=label_chess.ico \
    --add-data label_chess/VERSION:label_chess \
    --add-data $1/fen2pil/VERSION:fen2pil \
    --add-data $1/fen2pil/pieces/black/*:fen2pil/pieces/black \
    --add-data $1/fen2pil/pieces/white/*:fen2pil/pieces/white \
    --hidden-import='PIL._tkinter_finder'

