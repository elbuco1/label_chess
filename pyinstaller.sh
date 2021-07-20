# reset sqlite database
python3 start_app.py --reset_db --no_start

# remove .exe build artefacts
rm -r dist
rm -r build
rm label_chess-*.spec

# SITE_PACKAGES=pyinstaller_env/lib/python3.8/site-packages
# bash pyinstaller.sh ~/anaconda3/envs/label_chess/lib/python3.9/site-packages 0.0.1
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

