import itertools
from contextlib import contextmanager
from textwrap import dedent

import pytest
from gravitrips import Gravitrips, InvalidInput


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "moves, players, expected",
    (
        # Two players
        (0, 2, 0),
        (1, 2, 1),
        (2, 2, 0),
        (3, 2, 1),
        # Three players
        (0, 3, 0),
        (1, 3, 1),
        (2, 3, 2),
        (3, 3, 0),
        (4, 3, 1),
        (5, 3, 2),
    ),
)
def test_active_player_id(moves, players, expected):
    game = Gravitrips(players=players)
    game.moves = moves
    assert game.active_player_id == expected


@pytest.mark.parametrize(
    "moves, players, expected",
    (
        # Two players
        (0, 2, "A"),
        (1, 2, "B"),
        (2, 2, "A"),
        # Three players
        (0, 3, "A"),
        (1, 3, "B"),
        (2, 3, "C"),
        (3, 3, "A"),
        (4, 3, "B"),
        (5, 3, "C"),
    ),
)
def test_active_player_name(moves, players, expected):
    game = Gravitrips(players=players)
    game.moves = moves
    assert game.active_player_name == expected


@pytest.mark.parametrize(
    "stdin_str, expected_exception, expected_result",
    (
        ("-1", pytest.raises(InvalidInput, match="The input must be a number"), None),
        ("0", pytest.raises(InvalidInput, match="The input must be a number"), None),
        ("1", does_not_raise(), 1),
        ("7", does_not_raise(), 7),
        ("8", pytest.raises(InvalidInput, match="The input must be a number"), None),
        ("1000", pytest.raises(InvalidInput, match="The input must be a number"), None),
    ),
)
def test_request_input(monkeypatch, stdin_str, expected_exception, expected_result):
    game = Gravitrips()
    monkeypatch.setattr("builtins.input", lambda x: stdin_str)

    with expected_exception:
        assert expected_result == game.request_input()


def parse_grid(grid_text):
    def encode_cell(s):
        return None if s == "." else ord(s) - 65

    return [
        [encode_cell(col) for col in row]
        for row in reversed(grid_text.strip().split("\n"))
    ]


grid_north_line = dedent(
    """\
    .......
    .......
    A......
    A.....B
    A.....B
    A.....B
    """
)

grid_north_east_line = dedent(
    """\
    .......
    .......
    ...A...
    ..AB...
    .ABB...
    ABBBAAA
    """
)

grid_east_line = dedent(
    """\
    .......
    .......
    .......
    .......
    .......
    AAAABBB
    """
)

grid_south_east_line = dedent(
    """\
    .......
    .......
    ...A...
    ...BA..
    ...BBA.
    AAABBBA
    """
)


@pytest.mark.parametrize(
    "last_move, grid_text",
    (
        ((0, 3), grid_north_line),
        ((0, 0), grid_north_east_line),
        ((1, 1), grid_north_east_line),
        ((2, 2), grid_north_east_line),
        ((3, 3), grid_north_east_line),
        ((0, 0), grid_east_line),
        ((1, 0), grid_east_line),
        ((2, 0), grid_east_line),
        ((3, 0), grid_east_line),
        ((6, 0), grid_south_east_line),
        ((5, 1), grid_south_east_line),
        ((4, 2), grid_south_east_line),
        ((3, 3), grid_south_east_line),
    ),
)
def test_compute_winner(last_move, grid_text):
    game = Gravitrips()
    game.grid = parse_grid(grid_text)

    game.compute_winner(*last_move)

    assert game.winner == "A"


@pytest.mark.parametrize(
    "direction, last_move, grid_text, expected_cells",
    (
        (
            Gravitrips.DIRECTIONS[0],
            (0, 3),
            grid_north_line,
            {(0, 0), (0, 1), (0, 2), (0, 3)},
        ),
        (
            Gravitrips.DIRECTIONS[1],
            (0, 0),
            grid_north_east_line,
            {(0, 0), (1, 1), (2, 2), (3, 3)},
        ),
        (
            Gravitrips.DIRECTIONS[2],
            (0, 0),
            grid_east_line,
            {(0, 0), (1, 0), (2, 0), (3, 0)},
        ),
        (
            Gravitrips.DIRECTIONS[3],
            (6, 0),
            grid_south_east_line,
            {(6, 0), (5, 1), (4, 2), (3, 3)},
        ),
    ),
)
def test_get_last_connected_cells(direction, last_move, grid_text, expected_cells):
    game = Gravitrips()
    game.grid = parse_grid(grid_text)

    connected_cells = set(game.get_connected_cells(direction, *last_move))
    assert connected_cells == expected_cells


@pytest.mark.parametrize(
    "player_a_moves, player_b_moves, expected_winner",
    (
        ((1, 2, 3, 4, 5, 6, 7), (1, 2, 3, 4, 5, 6, 7), "A"),
        ((1, 2, 3, 4, 5, 6, 7), (2, 3, 4, 5, 6, 7, 1), "B"),
        ((7, 6, 5, 4, 3, 2, 1), (1, 2, 3, 4, 5, 6, 7), "A"),
        ((1, 1, 1, 1), (2, 2, 2, 2), "A"),
    ),
)
def test_game(monkeypatch, player_a_moves, player_b_moves, expected_winner):
    moves = list(reversed(list(itertools.chain(*zip(player_a_moves, player_b_moves)))))

    monkeypatch.setattr("builtins.input", lambda x: moves.pop())
    monkeypatch.setattr("os.system", lambda x: None)

    game = Gravitrips()
    game.start()

    assert game.winner == expected_winner
