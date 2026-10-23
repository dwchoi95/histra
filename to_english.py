"""Korean review draft -> English submission source: drop each Korean block that is directly followed by
'% EN: ' lines, strip the prefixes, remove kotex. Usage: python to_english.py main.tex > main.en.tex"""
import re, sys
out, buf = [], []
for line in open(sys.argv[1], encoding="utf-8").read().split("\n"):
    if line.startswith("% EN:"):
        buf = []                                   # the Korean version of this unit
        out.append(line[len("% EN:"):].lstrip(" ") if line[len("% EN:"):].startswith(" ") else line[len("% EN:"):])
        continue
    if line.strip() == "" or line.lstrip().startswith("%"):
        out += buf; buf = []
        if not re.search(r"[\uac00-\ud7a3]", line):   # Korean-only comments are dropped too
            out.append(line)
        continue
    buf.append(line)
out += buf
src = "\n".join(out)
src = re.sub(r"\\usepackage\{kotex\}[^\n]*\n(?:\s*%[^\n]*\n)?", "", src, count=1)
leftover = [l for l in src.split("\n") if re.search(r"[\uac00-\ud7a3]", l) and not l.lstrip().startswith("%")]
assert not leftover, leftover[:3]
sys.stdout.write(src)
