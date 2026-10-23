"""Fill the tables and figure data of main.tex from output/tables.tex (written by summarize.py); main.tex never inputs it.
Each '% rows:<name>' section of tables.tex replaces the lines between '% rows:<name>' and '% end rows' in main.tex.
Usage: python3 paper/src/fill_tables.py"""
import os
import re

PAPER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # <repo>/paper/

rows, cur = {}, None
for line in open(os.path.join(PAPER, "output", "tables.tex")):
    m = re.match(r"% rows:(\w+)", line)
    if m:
        cur = m.group(1)
        rows[cur] = []
    elif cur:
        rows[cur].append(line)
tex = open(os.path.join(PAPER, "main.tex")).read()
for name, rs in rows.items():
    pat = re.compile(rf"(% rows:{name}\n).*?(% end rows)", re.S)
    assert pat.search(tex), f"no '% rows:{name}' block in main.tex"
    tex = pat.sub(lambda m: m.group(1) + "".join(rs) + m.group(2), tex)
open(os.path.join(PAPER, "main.tex"), "w").write(tex)
print({k: len(v) for k, v in rows.items()})
