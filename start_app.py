#!/usr/bin/env python
# -*- coding: utf-8 -*-

from label_chess import models
from label_chess.app import ChessAnnotatorApp
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r', "--reset_db", help='Clear database',
        default=False, action='store_true')
    parser.add_argument(
        '-n', "--no_start", help="Don't start the app.",
        default=False, action='store_true')
    args = parser.parse_args()

    models.init_db(clear=args.reset_db)

    if not args.no_start:
        app = ChessAnnotatorApp()
        app.mainloop()
