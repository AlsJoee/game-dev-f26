"""Declared evaluation layouts, copied from midterms/alsjoee/README.md.

Row 0 is the top floor. Tiles: S start, E exit, . floor, space empty,
^ spikes, P pressure plate, G gate, # wall.
"""

ROOMS = {
    "A": [
        "S. .P.G.E",
    ],
    "B": [
        "S...  ..#",
        "#. ...^.#",
        "..#  ...#",
        "#^.....E#",
    ],
    "C": [
        "#...G..E",
        "#.. P###",
        "S..^####",
    ],
    "H": [
        "E..G..##",
        "###.P..#",
        "#.. ...#",
        "S..^ ..#",
    ],
}
