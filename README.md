# Gravitrips

A simple console-based [Connect Four](https://en.wikipedia.org/wiki/Connect_Four) game implementation.

## Requirements

Python 3.6+

## Usage

``` console
$ python gravitrips.py`
```

## Test

```console
$ pip install pytest
$ pytest
```

## Options

Run `python gravitrips.py --help` to get the information:

```
  --pieces-to-win PIECES_TO_WIN
                        A number of connected pieces required to win (default: 4)
  --players PLAYERS     Players count (default: 2)
  --columns COLUMNS     Game board columns size (default: 7)
  --rows ROWS           Game board rows size (default: 6)
  --debug               Enter to the post-mortem debugging if raised an exception (default: False)
```
