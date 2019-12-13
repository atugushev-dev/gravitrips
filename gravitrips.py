import argparse
import os
import pdb
import string
import sys
from typing import List, Optional, Set, Tuple


class InvalidParam(Exception):
    pass


class InvalidInput(Exception):
    pass


class GameOver(Exception):
    pass


class Gravitrips:
    PLAYER_NAMES = string.ascii_uppercase
    EMPTY_SPACE = "."
    CONNECTON_MARKER = "*"
    DIRECTIONS = (
        (0, 1),  # North
        (1, 1),  # Northeast
        (1, 0),  # East
        (1, -1),  # Southeast
    )

    def __init__(
        self,
        debug: bool = False,
        pieces_to_win: int = 4,
        players: int = 2,
        columns: int = 7,
        rows: int = 6,
    ) -> None:
        if players < 2:
            raise InvalidParam("Players must be at least two.")
        if pieces_to_win < 2:
            raise InvalidParam("Pieces to win must be at least two.")
        if rows < 1:
            raise InvalidParam("There must be at least one column.")
        if columns < 1:
            raise InvalidParam("There must be at least one row.")
        if players > len(self.PLAYER_NAMES):
            raise InvalidParam(
                f"Maximum number of players is {len(self.PLAYER_NAMES)}."
            )

        self.debug = debug
        self.pieces_to_win = pieces_to_win
        self.players = players
        self.columns = columns
        self.rows = rows

        self.moves = 0
        self.winner: Optional[str] = None
        self.connected_cells: Set[Tuple[int, int]] = set()
        self.column_mass = [0] * self.columns
        self.grid: List[List[Optional[int]]] = [
            [None for _ in range(self.columns)] for _ in range(self.rows)
        ]

    @property
    def active_player_id(self) -> int:
        return self.moves % self.players

    @property
    def active_player_name(self) -> str:
        return self.PLAYER_NAMES[self.active_player_id]

    def request_input(self) -> int:
        invalid_number_message = (
            f"The input must be a number between 1 and {self.columns}. Try again."
        )
        try:
            col = int(
                input(
                    f"\nPlayer {self.active_player_name}, "
                    f"enter a number of column> "
                )
            )
        except ValueError:
            raise InvalidInput(invalid_number_message)

        if not (1 <= col <= self.columns):
            raise InvalidInput(invalid_number_message)

        if self.column_mass[col - 1] >= self.rows:
            raise InvalidInput(f"The column {col} is full. Choose another one.")

        return col

    def turn(self) -> None:
        if self.moves >= self.columns * self.rows:
            raise GameOver("No moves are left. Withdraw.")

        # Get valid input
        while True:
            try:
                col = self.request_input()
                col -= 1  # user inputs 1..N, but we process 0..N-1
            except InvalidInput as exc:
                print(exc)
            else:
                break

        # Current column mass and row id
        row = self.column_mass[col]

        # Store player ID in grid
        self.grid[row][col] = self.active_player_id

        # Check the winner
        self.compute_winner(col, row)

        # Move on
        self.column_mass[col] += 1
        self.moves += 1

    def compute_winner(self, col: int, row: int) -> None:
        # Search connected cells all over directions (hr, vr, diag)
        for d in self.DIRECTIONS:
            connected_cells = self.get_connected_cells(d, col, row)

            if len(connected_cells) == self.pieces_to_win:
                self.winner = self.active_player_name
                self.connected_cells = set(connected_cells)
                return

    def get_connected_cells(
        self, direction: Tuple[int, int], col: int, row: int
    ) -> List[Tuple[int, int]]:
        forward_cells = self._get_connected_cells_inc(direction, col, row, step=1)
        backward_cells = self._get_connected_cells_inc(direction, col, row, step=-1)
        return backward_cells + forward_cells[1:]

    def _get_connected_cells_inc(
        self, direction: Tuple[int, int], col: int, row: int, step: int
    ) -> List[Tuple[int, int]]:
        cells = []
        while (
            0 <= col < self.columns
            and 0 <= row < self.rows
            and self.grid[row][col] == self.active_player_id
        ):
            cells.append((col, row))
            col += direction[0] * step
            row += direction[1] * step
        return cells

    def render_results(self) -> None:
        self.render_grid()
        print(f"\nPlayer {self.winner} won!")

    def start(self) -> None:
        try:
            self.loop()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
        except GameOver as exc:
            print(exc)
        except Exception:
            if self.debug:
                pdb.post_mortem()
            raise

    def loop(self) -> None:
        while self.winner is None:
            self.render_grid()
            self.turn()

        self.render_results()

    def render_cell(self, col: int, row: int) -> str:
        player_id = self.grid[row][col]
        if player_id is None:
            return self.EMPTY_SPACE
        elif (col, row) in self.connected_cells:
            return self.CONNECTON_MARKER
        return self.PLAYER_NAMES[player_id]

    def render_grid(self) -> None:
        os.system("clear" if os.name == "posix" else "cls")

        column_width = len(str(self.columns - 1))
        columns_header = " ".join(
            str(col + 1).zfill(column_width) for col in range(self.columns)
        )
        print(columns_header)

        for row in reversed(range(self.rows)):
            print(
                "".join(
                    " ".join(
                        "{0:^{1}}".format(self.render_cell(col, row), column_width)
                        for col in range(self.columns)
                    )
                )
            )

        print(columns_header)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pieces-to-win", type=int, default=4)
    parser.add_argument("--players", type=int, default=2)
    parser.add_argument("--columns", type=int, default=7)
    parser.add_argument("--rows", type=int, default=6)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)

    try:
        game = Gravitrips(**vars(args))
        game.start()
    except InvalidParam as exc:
        print(f"Invalid param: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
