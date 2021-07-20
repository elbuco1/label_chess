# reset sqlite database
python3 start_app.py --reset_db --no_start

# remove .exe build artefacts
rm -r dist
rm -r build
rm start_app.spec

# SITE_PACKAGES=pyinstaller_env/lib/python3.8/site-packages
# bash pyinstaller.sh ~/anaconda3/envs/label_chess/lib/python3.9/site-packages
# create app
pyinstaller  start_app.py \
    --add-data label_chess/VERSION:label_chess \
    --add-data ./db.sqlite:. \
    --add-data $1/fen2pil/VERSION:fen2pil \
    --add-data $1/fen2pil/pieces/black/*:fen2pil/pieces/black \
    --add-data $1/fen2pil/pieces/white/*:fen2pil/pieces/white \
    --hidden-import='PIL._tkinter_finder'
