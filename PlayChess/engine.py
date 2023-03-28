import random

from chess import BaseBoard, Piece, piece_symbol, square
import chess

import symbol
# Milo is trash
# Quinn best chess player of all time

global abPruning
global count


def evaluate_position(board, fen):
    """ Evaluates the position of the board based on material
    :param fen:
    :return: evaluation
    """
    if board.is_checkmate():
        if board.outcome().winner:
            return 49
        else:
            return -49

    if board.is_stalemate():
        return 0

    valuations = {'K': 100, 'Q': 9, 'R': 5, 'N': 3, 'B': 3, 'P': 1,  # White
                  'k': -100, 'q': -9, 'r': -5, 'n': -3, 'b': -3, 'p': -1,  # Black
                  }
    evaluation = 0
    for s in fen:
        # Only look at the characters that are actually in the dictionary
        if s in valuations:
            evaluation += valuations[s]
        # Only look at the part of fen that relates to pieces
        if s == ' ':
            break

    return evaluation


def find_depth_move(board, depth):
    global abPruning
    global count
    abPruning = {}
    [abPruning.setdefault(i+1, []) for i in range(depth)]
    count = 0
    ans = find_depth_move_recursion(board, 0, depth)
    print(count)
    return ans


def find_depth_move_recursion(board, depth, returnDepth):
    """ Checks position evaluation out of all possibilities depth moves forward and chooses best move
    :param b:
    :return move:
    """
    # We want to set the pruning number, the given depth can have a max
    # or min value associated with it depending on whose turn it is,
    # in which we can prune (not search) any branches if they are lower than
    # the max or higher than the min number.
    # Special cases arise based on quasi-stability of the board;
    # for now, we will ignore this.
    global abPruning
    global count
    if depth % 2 == 1:
        # Black just moved, favor negative values
        if not abPruning[depth]:
            abPruning[depth] = evaluate_position(board, board.fen())
        else:
            abPruning[depth] = min(
                abPruning[depth], evaluate_position(board, board.fen()))
    else:
        if depth != 0:
            # White just moved, favor positive values
            if not abPruning[depth]:
                abPruning[depth] = evaluate_position(board, board.fen())
            else:
                abPruning[depth] = max(
                    abPruning[depth], evaluate_position(board, board.fen()))

    searchTree = True
    if depth != 0:
        if abPruning[depth] != evaluate_position(board, board.fen()):
            searchTree = False  # If you want to test without alpha-beta pruning, set this to True!

    if depth == returnDepth or not searchTree:
        return evaluate_position(board, board.fen())
    count += 1

    moves = list(board.legal_moves)
    vs = {}
    [vs.setdefault(i, []) for i in range(-50, 50, 1)]

    for i, move in zip(range(len(moves)), moves):
        board.push(move)
        v = find_depth_move_recursion(board, depth+1, returnDepth)
        vs[v].append(move)
        board.pop()

    for i in range(-50, 50, 1):
        if not vs[i]:
            vs.pop(i)

    if depth == 0:
        if board.turn:
            return random.choice(vs[max(vs)])
        else:
            return random.choice(vs[min(vs)])
    else:
        if board.turn:
            return max(vs)
        else:
            return min(vs)

# Determines Stability
# New engine must always evaluate at least two moves ahead
# New engine must always evaluate positions where this function returns 1 (UNLESS PAST 10 DEPTH)
# Overall depth will vary from 2-10 but be much quicker to calculate


def not_stable(board: BaseBoard, color: chess.Color):
    """
    Returns 1 if not quasi stable
        - If any piece is attacked by another of lower value
        - If any piece has more attackers than defenders
        - If any check exists from opponent
    Returns 0 if quasi stable
        - None of the above
    :param board:
    :return: 1 | 0
    """
    valuations = {'K': 100, 'Q': 9, 'R': 5, 'N': 3, 'B': 3, 'P': 1,  # White
                  'k': -100, 'q': -9, 'r': -5, 'n': -3, 'b': -3, 'p': -1,  # Black
                  }

    # Edge cases (need to be dealt with externally i.e: display game result and such)
    if board.is_check() or board.is_stalemate() or board.is_fivefold_repetition() or board.is_seventyfive_moves() or board.is_insufficient_material() or board.is_checkmate():
        return 1
    for square in board.pieces(color=color):
        attackers = (valuations[Piece.symbol(board.piece_type_at(sq))]
                     for sq in board.attackers(not color, square))
        defenders = (valuations[Piece.symbol(board.piece_type_at(sq))]
                     for sq in board.attackers(color, square))
        if len(attackers) > len(defenders):
            return 1
        if len(attackers) < len(defenders):
            return 0
        if len(attackers) == len(defenders):
            if attackers[0] > valuations[Piece.symbol(board.piece_type_at(square))]:
                return 1
            for i in range(1, attackers):
                if (attackers[i] > defenders[i-1]):
                    return 1
    return 0
