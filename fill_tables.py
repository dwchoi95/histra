"""Fill the tables and figure data of main.tex from output/summary/tables.tex (written by src/experiments/summarize.py).
Each '% rows:<name>' section of tables.tex replaces the lines between '% rows:<name>' and '% end rows' in main.tex.
Usage (from the repository root): python3 paper/fill_tables.py"""
import re

rows, cur = {}, None
for line in open("output/summary/tables.tex"):
    m = re.match(r"% rows:(\w+)", line)
    if m:
        cur = m.group(1)
        rows[cur] = []
    elif cur:
        rows[cur].append(line)
tex = open("paper/main.tex").read()
for name, rs in rows.items():
    pat = re.compile(rf"(% rows:{name}\n).*?(% end rows)", re.S)
    assert pat.search(tex), f"no '% rows:{name}' block in main.tex"
    tex = pat.sub(lambda m: m.group(1) + "".join(rs) + m.group(2), tex)
open("paper/main.tex", "w").write(tex)
print({k: len(v) for k, v in rows.items()})
