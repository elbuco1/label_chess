from PIL import Image, ImageDraw
import numpy as np
import os
from chess import pgn as c_pgn
import chess
import cv2


def get_chessboard_pattern(nb_squares=8):
    """Generate a 2d array nb_squares* nb_squares
    with zeros and ones representing a chessboard. 
    The pattern is the one of the standard chessboard.

    Args:
        nb_squares (int): nb of squares per side.
            Defaults to 8

    Returns:
        np.ndarray: binary representation of the chessboard.
            Ones denote the dark squares.
            Zeros denote the light squares.
    """
    x = np.zeros((nb_squares, nb_squares), dtype=int)
    x[1::2, ::2] = 1
    x[::2, 1::2] = 1
    return x


def create_empty_board(board_size=480, nb_squares=8,
                       light_color=(255, 253, 208), dark_color=(76, 153, 0)):
    """Generate PIL image of a chessboard.

    Args:
        board_size (int): image width and height (in pixels). Should be
            divisible by nb_squares. Defaults to 480.
        nb_squares (int, optional): nb of squares per side. Defaults to 8.
        light_color (tuple, optional): RGB color for light squares.
            Defaults to (255, 253, 208).
        dark_color (tuple, optional): RGB color for dark squares.
            Defaults to (76, 153, 0).

    Raises:
        ValueError: if the board_size is not divisible by nb_squares

    Returns:
        PIL.Image: empty chessboard image
    """
    if board_size % nb_squares != 0:
        raise ValueError(
            f"Board size must be divisible by {nb_squares}. Got {board_size}.")
    board = Image.new('RGB', (board_size, board_size), light_color)
    square_size = int(board_size/nb_squares)
    dark_square = Image.new('RGB', (square_size, square_size), dark_color)

    chessboard_pattern = get_chessboard_pattern(nb_squares)
    for i in range(nb_squares):
        for j in range(nb_squares):
            is_dark = chessboard_pattern[i][j]
            if is_dark:
                top_left = [j * square_size, i * square_size]
                bottom_right = [(j+1) * square_size, (i+1) * square_size]
                board.paste(dark_square, box=(*top_left, *bottom_right))
    return board


def load_pieces_images(dir_path, extension="png"):
    """Load all chess pieces images in a dict.
    The pieces names are: 
    ["B", "K", "N", "p", "Q", "R"] for
    [bishop, king, knight, pawn, queen, rook]

    They are prefixed with "b" for black pieces and
    with "w" for white pieces.

    * "bB" means: black bishop

    The filename for the black bishop image is
    assumed to be bB.[extension]

    Args:
        dir_path (str): directory where pieces images are saved
        extension (str, optional): image files extensions. Defaults to "png".

    Returns:
        dict: mapping of piece name to PIL.Image of the piece
    """
    pieces_names = ["B", "K", "N", "p", "Q", "R"]
    white_pieces = [f"w{name}" for name in pieces_names]
    black_pieces = [f"b{name}" for name in pieces_names]
    pieces_names = white_pieces + black_pieces

    pieces = {}
    for piece in pieces_names:
        piece_file_path = os.path.join(dir_path, f"{piece}.{extension}")
        piece_img = Image.open(piece_file_path)
        piece_img = piece_img.convert('RGBA')
        pieces[piece] = piece_img
    return pieces


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


def fen_to_array(fen):
    """Transform a FEN representation to a two
    dimensional numpy array representing the chess
    board with the pieces positions as strings.

    Args:
        fen (str): fen representation of a chessboard

    Returns:
        np.ndarray: 2d representation of array and pieces
    """
    ascii_fen = chess.Board(fen).__str__()
    ascii_fen = ascii_fen.split("\n")
    array_fen = np.array([row.split(" ") for row in ascii_fen])
    return array_fen


def rename_pieces(board_array):
    """Change name of pieces in array representation.
    All pieces name to uppercase. And prefixed with
    a lowercased "b" for black pieces and with a
    lowercased "w" for white pieces. This fonction is
    useful to interface functions fen_to_array and 
    draw_pieces.

    Args:
        board_array (np.ndarray): 2d representation of array and pieces
            as outputed by fen_to_array.

    Returns:
        np.ndarray: 2d representation of array and pieces
    """
    board_array = board_array.astype("<U2")
    for i in range(len(board_array)):
        for j in range(len(board_array)):
            square = board_array[i, j]
            if square != ".":
                if square.isupper():
                    if square == "P":
                        square = square.lower()
                    square = "w" + square
                else:
                    if square != "p":
                        square = square.upper()
                    square = "b" + square
            board_array[i, j] = square
    return board_array


def draw_pieces(board_img, pieces, board_array, nb_squares=8):
    """Draw pieces on an empty chessboard.

    Args:
        board_img (PIL.Image): empty chessboard image
        pieces (dict): mapping of piece name to PIL.Image of the piece.
            Images must have transparency as background.
        board_array (np.ndarray): 2d representation of array and pieces
        nb_squares (int, optional): nb of squares on a side of the chessboard.
            Defaults to 8.

    Raises:
        ValueError: if the board_size is not divisible by nb_squares

    Returns:
        PIL.Image: chess board with pieces placed as specified in
            board_array
    """
    board_size = board_img.size[0]
    if board_size % nb_squares != 0:
        raise ValueError(
            f"Board size must be divisible by {nb_squares}. Got {board_size}.")
    square_size = int(board_size/nb_squares)
    for i in range(len(board_array)):
        for j in range(len(board_array)):
            piece = board_array[i, j]
            if piece != ".":
                piece_img = pieces[piece]
                top_left = (j * square_size, i * square_size)
                board_img.paste(piece_img, box=top_left, mask=piece_img)
    return board_img


def get_game_board_images(pgn_path, pieces_path):
    """Get PIL.Image representations of chessgame
    positions from a pgn file.

    Args:
        pgn_path (str): path to pgn file representation of
            a chess game.
        pieces_path (str): directory where pieces images are saved

    Returns:
        list: list of PIL.Image representing the positions of the
            chessgame ordered chronologically.
        list: list of fens (strings)
    """
    fens = pgn_to_fens(pgn_path)
    board = create_empty_board()
    pieces = load_pieces_images(pieces_path)
    # TODO board size based on piece size
    images = []
    for fen in fens:
        board_copy = board.copy()
        board_array = fen_to_array(fen)
        board_array = rename_pieces(board_array)
        board_copy = draw_pieces(board_copy, pieces, board_array)
        images.append(board_copy)
    return images, fens


def display_game_as_image(images, presskey=False):
    """Display positions images of a chess game
    sequentially.

    Args:
        images (list of PIL.Image): images of positions
        presskey (bool, optional): If True, it is required
            to press a key to pass to the next image. Else
            it is done automatically after 300 ms.
            Defaults to False.
    """
    for img in images:
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow('frame', img)
        if presskey:
            key = cv2.waitKey(0) & 0xFF
        else:
            key = cv2.waitKey(300) & 0xFF
        if key == ord('q'):
            print("Stop simulation.")
            break
    cv2.destroyAllWindows()


# if __name__ == "__main__":
#     pieces_path = "resources/pieces"
#     pgn_path = "data/raw/kramnik_carlsen_salman2019"

#     images, _ = get_game_board_images(pgn_path, pieces_path)
#     display_game_as_image(images, True)
