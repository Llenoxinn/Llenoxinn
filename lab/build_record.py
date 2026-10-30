#!/usr/bin/env python3
"""Generate the lab's researcher record from verified portfolio content."""
from notebook import ASSETS, THEMES, Typesetter, svg_doc

FIELDS = [
    ('Researcher', 'Dexter Juevesano'),
    ('Education', 'BS Computer Science · UP Cebu · DOST scholar'),
    ('Based in', 'Cebu, Philippines · UTC+8'),
    ('Exploring', 'AI software development · cybersecurity · bioinformatics'),
    ('Method', 'Build things. Break them. Write down what happened.'),
]


def card(theme):
    t, ts = THEMES[theme], Typesetter('record')
    body = ts.text('Researcher record', 'display', 34, 22, 44, t['ink'])[0]
    body += f'<path d="M22 62H818" stroke="{t["edge"]}"/>'
    for i, (label, value) in enumerate(FIELDS):
        y = 99 + 38 * i
        body += ts.text(label, 'label', 15, 22, y, t['muted'])[0]
        body += ts.text(value, 'text', 18, 158, y, t['ink'])[0]
    return svg_doc(840, 276, ts.defs_svg() + body, '; '.join(f'{k}: {v}' for k, v in FIELDS))


if __name__ == '__main__':
    for theme in THEMES:
        (ASSETS / f'record-{theme}.svg').write_text(card(theme), encoding='utf-8')
    print('wrote researcher records')
