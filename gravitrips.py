import os
import sys
import argparse
import pdb
from typing import List


class GameOver(Exception):
    pass


class Gravitrips:
    MAX_X_AXIS = 7
    MAX_Y_AXIS = 6

    CHIPS = ("🔵", "🔴")
    PLAYER_NAMES = ("Player A", "Player B")
    EMPTY_SPACE = "⚪"

    def __init__(self, debug=False):
        self.debug = debug
        self.turns = 0
        self.total_players = 2
        self.last_input = None
        self.field = [0] * self.MAX_X_AXIS
        self.winner = None
        self.matrix = [
            [None for _ in range(self.MAX_X_AXIS)] for _ in range(self.MAX_Y_AXIS)
        ]

    @property
    def active_player_id(self) -> int:
        return self.turns % self.total_players

    @property
    def active_player_name(self):
        return f"{self.CHIPS[self.active_player_id]} {self.PLAYER_NAMES[self.active_player_id]}"

    def request_input(self):
        while True:
            int_err_msg = (
                f"The input must be a number between "
                f"0 and {self.MAX_X_AXIS}. Try again."
            )
            try:
                x = int(
                    input(f"\n{self.active_player_name}, enter a number of column> ")
                )
            except ValueError:
                print(int_err_msg)
                continue

            if not (0 <= x <= self.MAX_X_AXIS - 1):
                print(int_err_msg)
                continue

            if self.field[x] >= self.MAX_Y_AXIS:
                print(f"The column {x} is full. Choose another one.")
                continue

            return x

    def turn(self):
        self.last_input = x = self.request_input()
        self.matrix[self.field[x]][x] = self.active_player_id

        self.check_winner()

        self.field[x] += 1
        self.turns += 1

    def check_winner(self):
        directions = (
            (0, 1),  # North
            (1, 1),  # Northeast
            (1, 0),  # East
            (1, -1),  # Southeast
        )

        for d in directions:
            x = self.last_input
            y = self.field[x]

            forward_count = self.count_connected_cells(d, x, y, 1)
            backward_count = self.count_connected_cells(d, x, y, -1)

            if forward_count + backward_count - 1 == 4:
                self.winner = self.active_player_id
                return

    def count_connected_cells(self, direction, x, y, step):
        count = 0
        while (
            self.matrix[y][x] == self.active_player_id
            and 0 <= x < self.MAX_X_AXIS
            and 0 <= x < self.MAX_Y_AXIS
        ):
            count += 1
            x += direction[0] * step
            y += direction[1] * step
        return count

    def display_results(self):
        os.system("clear")
        self.render_field()
        print(f"\n{self.active_player_name} won!")

    def start(self):
        try:
            self.loop()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
        except Exception:
            if self.debug:
                pdb.post_mortem()
            raise

    def loop(self):
        while self.winner is None:
            os.system("clear")
            self.render_field()
            self.turn()

        self.display_results()

    def render_cell(self, x, y):
        if self.matrix[y][x] is None:
            return self.EMPTY_SPACE
        return self.CHIPS[self.matrix[y][x]]

    def render_field(self):
        # print(" ".join(str(x) for x in range(self.MAX_X_AXIS)))
        for y in reversed(range(self.MAX_Y_AXIS)):
            print(
                "".join(
                    " ".join(self.render_cell(x, y) for x in range(self.MAX_X_AXIS))
                )
            )
        # print(" ".join(str(x) for x in range(7)))


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", type=int, default=2)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)

    Gravitrips(debug=args.debug).start()
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
