"""Original pixel art from Dexter's portfolio-fin/lib/pixel-art.ts, and the 5×7 display face.

Sprite cells: P = paper, L = lavender, N = neon, D = deep (the portfolio's names); the lab
draws them in amber phosphor through notebook.SPRITE. Empty cells are transparent.
"""

SCIENTIST = [
    '.....N..NN......', '....NNNNNNNN....', '...NNNNNNNNNN...',
    '..NNDPPDDPPDNN..', '..NNDPPDDPPDNN..', '..NLLLLLLLLLLN..',
    '..NLLDLLLLDLLN..', '...LLLLLLLLLL...', '....LLLDDLLL....',
    '...PPPLNNLPPP...', '..PPPPPLNNLPPPP.', '.LPPPPPPNNPPPPPL',
    '.LPNPPPPPPPPPPPL', '..PPPPPPPPPPPP..', '..PPPPPPPPPPPP..',
    '...NN....NN.....', '..NN......NN....', '.PPP......PPP...',
]
COIL = [
    '....PPPPPPPP....', '..PPPPPPPPPPPP..', '.PPPPPPPPPPPPPP.',
    '.LLLLLLLLLLLLLL.', '..LLLLLLLLLLLL..', '.......LL.......',
    '......PPPP......', '......L..L......', '......PPPP......',
    '......L..L......', '......PPPP......', '......L..L......',
    '......PPPP......', '......L..L......', '......PPPP......',
    '......L..L......', '......PPPP......', '....LLLLLLLL....',
    '....L......L....', '....LLLLLLLL....', '...PPPPPPPPPP...',
    '..PPPPPPPPPPPP..', '..PPPPPPPPPPPP..',
]


# ---- more sprites from portfolio-fin/lib/pixel-art.ts
HEAD = SCIENTIST[:9]
COAT = [
    '...PPPLNNLPPP...', '..PPPPPLNNLPPPP.', '.PPPPPPPNNPPPPP.',
    '.PPNPPPPPPPPPPP.', '..PPPPPPPPPPPP..', '..PPPPPPPPPPPP..',
]
PASS = ['....NN..NN......', '.....NNNN.......', '....PPPPPP......']
# Waving: the right hand swings between two positions.
WAVE_A = HEAD + ['...PPPLNNLPPP.LL', '..PPPPPLNNLPPPPL', '.PPPPPPPNNPPPPP.', '.PPNPPPPPPPPPPP.'] + COAT[4:] + PASS
WAVE_B = HEAD[:8] + ['....LLLDDLLL..LL', '...PPPLNNLPPP.L.', '..PPPPPLNNLPPPPL', '.PPPPPPPNNPPPPP.',
                     '.PPNPPPPPPPPPPP.'] + COAT[4:] + PASS
FLASK = [
    '....LLLL....', '....L..L....', '....L..L....', '....L..L....', '...L....L...', '...L....L...',
    '..L..PP..L..', '..LNNNNNNL..', '.LNNNPNNNNL.', '.LNNNNNNPNL.', 'LNNPNNNNNNNL', 'LNNNNNNNNNNL',
    'LLLLLLLLLLLL',
]
_TESLA = [
    '..PPPPPPPP..', '.PPPPPPPPPP.', '..LLLLLLLL..', '.....LL.....', '....PPPP....', '....L..L....',
    '....PPPP....', '....L..L....', '....PPPP....', '....L..L....', '....PPPP....', '...LLLLLL...',
    '..PPPPPPPP..', '.PPPPPPPPPP.',
]
TESLA_A = ['N..........N', '.N.PPPPPP.N.'] + _TESLA
TESLA_B = ['.N........N.', 'N..PPPPPP..N'] + _TESLA
ORB_A = ['..N..N..', '...NN...', '.NNPPNN.', 'NNPPPPNN', 'NNPPPPNN', '.NNPPNN.', '...NN...', '..N..N..']
ORB_B = ['N......N', '.N.NN.N.', '..NPPN..', '.NPPPPN.', '.NPPPPN.', '..NPPN..', '.N.NN.N.', 'N......N']
ENVELOPE = [r.replace('#', 'P') for r in [
    '################', '##............##', '#.#..........#.#', '#..#........#..#', '#...#......#...#',
    '#....#....#....#', '#.....####.....#', '#..............#', '#..............#', '#..............#',
    '#..............#', '################']]
TROPHY = ['NPPPPPPPPN', 'NPPPPPPPPN', 'P.PPPPPP.P', 'P.PPPPPP.P', '.PPPPPPPP.',
          '..PPPPPP..', '....LL....', '....LL....', '...LLLL...', '..PPPPPP..']
# A silver medal on its ribbon, for a podium finish that is not first place.
MEDAL = ['NN......NN', '.NN....NN.', '..NN..NN..', '...NNNN...', '....LL....', '..LLLLLL..', '.LPPPPPPL.',
         'LPPPLLPPPL', 'LPPLPPLPPL', 'LPPPPLPPPL', 'LPPPLPPPPL', 'LPPLLLLPPL', '.LPPPPPPL.', '..LLLLLL..']
# The trophy's second frame: a lavender glint runs down the cup.
TROPHY_GLINT = ['NPPPPPPPPN', 'NPPLPPPPPN', 'P.PPLPPP.P', 'P.PPPLPP.P', '.PPPPPPPP.',
                '..PPPPPP..', '....LL....', '....LL....', '...LLLL...', '..PPPPPP..']

# ---- handcrafted 16×16 trophy shelf awards (distinct silhouettes + crisp high-contrast engraving)
CUP_HACK = [
    '..PPPPPPPPPPPL..', 'NNLPPPPPPPPPPLNN', 'N.PPPPPPPPPLLL.N', 'N.PPPPPPPPPLLL.N',
    'N.LPPPPPPPLLLN.N', '.NNPPPPPPPLLLNN.', '...LPPPPPPLLN...', '....LPPPPLLN....',
    '.....LPPLLN.....', '......PPLN......', '......PPLN......', '.....PPPLLN.....',
    '...PPPPPPPPLL...', '..LPPDDDDDDLLN..', '..LPPDDDDDDLLN..', '..NNNNNNNNNNNN..',
]
CUP_CTF = [
    '..PPPPPPPPPPPL..', '.NLPPPPPPPPPPLN.', '.N.PPPDDDDPPL.N.', '.N.PPPDDDDPPL.N.',
    '.NNPPPDDPPPLLNN.', '...PPPDPPPPLL...', '...LPPPPPPLLN...', '....LPPPPLLN....',
    '.....LPPLLN.....', '......PPLN......', '......PPLN......', '.....PPPLLN.....',
    '...PPPPPPPPLL...', '..LPPDDDDDDLLN..', '..LPPDDDDDDLLN..', '..NNNNNNNNNNNN..',
]
MEDAL_2 = [
    '..NNN......NNN..', '..NLNN....NNLN..', '...NLNN..NNLN...', '....NLNNNNLN....',
    '.....LPPPPL.....', '....PPPPPPPL....', '...PPLLLLLLPN...', '..PPLPDDDDPLPN..',
    '..PPLPPPPDPLPN..', '..PPLPDDDDPLPN..', '..PPLPDPPPPLPN..', '..PPLPDDDDPLPN..',
    '...PPLLLLLLPN...', '....LPPPPPPL....', '...NN.LLLL.NN...', '..NNNNNNNNNNNN..',
]


def sheen_mask(rows, offset, max_row=12):
    """Return a sparse grid containing only 'S' pixels along diagonal c + r in (offset, offset + 1)."""
    out = []
    for r, row in enumerate(rows):
        out.append("".join(
            "S" if r <= max_row and ch in ("P", "L") and (c + r) in (offset, offset + 1) else "."
            for c, ch in enumerate(row)
        ))
    return out


def _monitor(shift):
    """A small lab monitor with a sweeping phosphor ECG trace: bright head, lavender tail."""
    w, h = 14, 9
    beat = {0: 5, 1: 5, 2: 5, 3: 4, 4: 2, 5: 7, 6: 5, 7: 5, 8: 5, 9: 5, 10: 5, 11: 5}
    rows = []
    for y in range(h):
        if y in (0, h - 1):
            rows.append("L" * w)
            continue
        row = ["L"] + ["D"] * (w - 2) + ["L"]
        for x in range(1, w - 1):
            col = x - 1
            if beat[col] == y:
                dist = (shift - col) % 12
                if dist == 0:
                    row[x] = "P"       # bright phosphor write-head
                elif dist <= 3:
                    row[x] = "L"       # glowing afterglow tail
                elif dist <= 7:
                    row[x] = "N"       # fading trace
        rows.append("".join(row))
    return rows + ["....LLLLLL....", "...LLLLLLLL..."]


MONITOR_A, MONITOR_B = _monitor(4), _monitor(8)
MONITOR_FRAMES = [_monitor(s) for s in range(12)]


# ---- the 5×7 display face: amber dot-matrix numerals and words on the instrument screens.
# HD44780-style glyphs, so digits never misread at small sizes. '#' is a lit dot; glyphs
# narrower than five columns set proportionally (one dark column between glyphs).
def _face(spec):
    out = {}
    for block in spec.strip().split("\n\n"):
        key, *rows = block.split("\n")
        out[key[1:-1]] = rows
    return out


DOTFONT = _face("""
[0]
.###.
#...#
#...#
#...#
#...#
#...#
.###.

[1]
..#..
.##..
..#..
..#..
..#..
..#..
.###.

[2]
.###.
#...#
....#
...#.
..#..
.#...
#####

[3]
#####
...#.
..#..
...#.
....#
#...#
.###.

[4]
...#.
..##.
.#.#.
#..#.
#####
...#.
...#.

[5]
#####
#....
####.
....#
....#
#...#
.###.

[6]
..##.
.#...
#....
####.
#...#
#...#
.###.

[7]
#####
....#
...#.
..#..
.#...
.#...
.#...

[8]
.###.
#...#
#...#
.###.
#...#
#...#
.###.

[9]
.###.
#...#
#...#
.####
....#
...#.
.##..

[A]
.###.
#...#
#...#
#...#
#####
#...#
#...#

[B]
####.
#...#
#...#
####.
#...#
#...#
####.

[C]
.###.
#...#
#....
#....
#....
#...#
.###.

[D]
###..
#..#.
#...#
#...#
#...#
#..#.
###..

[E]
#####
#....
#....
####.
#....
#....
#####

[F]
#####
#....
#....
####.
#....
#....
#....

[G]
.###.
#...#
#....
#.###
#...#
#...#
.####

[H]
#...#
#...#
#...#
#####
#...#
#...#
#...#

[I]
###
.#.
.#.
.#.
.#.
.#.
###

[J]
..###
...#.
...#.
...#.
...#.
#..#.
.##..

[K]
#...#
#..#.
#.#..
##...
#.#..
#..#.
#...#

[L]
#....
#....
#....
#....
#....
#....
#####

[M]
#...#
##.##
#.#.#
#.#.#
#...#
#...#
#...#

[N]
#...#
#...#
##..#
#.#.#
#..##
#...#
#...#

[O]
.###.
#...#
#...#
#...#
#...#
#...#
.###.

[P]
####.
#...#
#...#
####.
#....
#....
#....

[Q]
.###.
#...#
#...#
#...#
#.#.#
#..#.
.##.#

[R]
####.
#...#
#...#
####.
#.#..
#..#.
#...#

[S]
.####
#....
#....
.###.
....#
....#
####.

[T]
#####
..#..
..#..
..#..
..#..
..#..
..#..

[U]
#...#
#...#
#...#
#...#
#...#
#...#
.###.

[V]
#...#
#...#
#...#
#...#
#...#
.#.#.
..#..

[W]
#...#
#...#
#...#
#.#.#
#.#.#
#.#.#
.#.#.

[X]
#...#
#...#
.#.#.
..#..
.#.#.
#...#
#...#

[Y]
#...#
#...#
#...#
.#.#.
..#..
..#..
..#..

[Z]
#####
....#
...#.
..#..
.#...
#....
#####

[a]
.....
.....
.###.
....#
.####
#...#
.####

[b]
#....
#....
#.##.
##..#
#...#
#...#
####.

[c]
.....
.....
.###.
#....
#....
#...#
.###.

[d]
....#
....#
.##.#
#..##
#...#
#...#
.####

[e]
.....
.....
.###.
#...#
#####
#....
.###.

[f]
..##.
.#..#
.#...
###..
.#...
.#...
.#...

[g]
.....
.####
#...#
#...#
.####
....#
.###.

[h]
#....
#....
#.##.
##..#
#...#
#...#
#...#

[i]
.#.
...
##.
.#.
.#.
.#.
###

[j]
...#
....
..##
...#
...#
#..#
.##.

[k]
#...
#...
#..#
#.#.
##..
#.#.
#..#

[l]
##.
.#.
.#.
.#.
.#.
.#.
###

[m]
.....
.....
##.#.
#.#.#
#.#.#
#...#
#...#

[n]
.....
.....
#.##.
##..#
#...#
#...#
#...#

[o]
.....
.....
.###.
#...#
#...#
#...#
.###.

[p]
.....
.....
####.
#...#
####.
#....
#....

[q]
.....
.....
.##.#
#..##
.####
....#
....#

[r]
.....
.....
#.##.
##..#
#....
#....
#....

[s]
.....
.....
.###.
#....
.###.
....#
####.

[t]
.#..
.#..
###.
.#..
.#..
.#.#
..#.

[u]
.....
.....
#...#
#...#
#...#
#..##
.##.#

[v]
.....
.....
#...#
#...#
#...#
.#.#.
..#..

[w]
.....
.....
#...#
#...#
#.#.#
#.#.#
.#.#.

[x]
.....
.....
#...#
.#.#.
..#..
.#.#.
#...#

[y]
.....
.....
#...#
#...#
.####
....#
.###.

[z]
.....
.....
#####
...#.
..#..
.#...
#####

[ ]
...
...
...
...
...
...
...

[.]
.
.
.
.
.
.
#

[,]
..
..
..
..
..
.#
#.

[:]
.
.
#
.
.
#
.

[']
#
#
.
.
.
.
.

[!]
#
#
#
#
#
.
#

[-]
....
....
....
####
....
....
....

[+]
.....
..#..
..#..
#####
..#..
..#..
.....

[/]
.....
....#
...#.
..#..
.#...
#....
.....

[%]
##...
##..#
...#.
..#..
.#...
#..##
...##

[#]
.#.#.
.#.#.
#####
.#.#.
#####
.#.#.
.#.#.

[@]
.###.
#...#
#.###
#.#.#
#.###
#....
.###.

[?]
.###.
#...#
....#
...#.
..#..
.....
..#..

[(]
..#
.#.
#..
#..
#..
.#.
..#

[)]
#..
.#.
..#
..#
..#
.#.
#..

[_]
.....
.....
.....
.....
.....
.....
#####

[×]
.....
#...#
.#.#.
..#..
.#.#.
#...#
.....
""")
