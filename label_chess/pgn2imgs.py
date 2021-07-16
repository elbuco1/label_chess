#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chess import pgn as c_pgn
from fen2pil import draw


def pgn_to_fens(pgn_path):
    """Get sequence of board's fen representations
    from a pgn file.

    Args:
        pgn_path (str): path to pgn file

    Returns:
        list: list of fen representations, one per move.
    """
    fens = []
    with open(pgn_path, "r") as pgn_file:
        game = c_pgn.read_game(pgn_file)
        board = game.board()
        fens.append(board.board_fen())
        for move in game.mainline_moves():
            board.push(move)
            fens.append(board.board_fen())
    return fens


def get_game_board_images(pgn_path, board_size=480):
    """Get PIL.Image representations of chessgame
    positions from a pgn file.

    Args:
        pgn_path (str): path to pgn file representation of
            a chess game.
        board_size (int): width of the board image in pixels

    Returns:
        list: list of PIL.Image representing the positions of the
            chessgame ordered chronologically.
        list: list of fens (strings)
    """
    fens = pgn_to_fens(pgn_path)
    images = []
    for fen in fens:
        img = draw.transform_fen_pil(
            fen=fen,
            board_size=board_size
        )
        images.append([fen, img])
    return images



# if __name__ == "__main__":
#     pieces_path = "resources/pieces"
#     pgn_path = "data/raw/kramnik_carlsen_salman2019"

#     images, _ = get_game_board_images(pgn_path, pieces_path)
#     display_game_as_image(images, True)
