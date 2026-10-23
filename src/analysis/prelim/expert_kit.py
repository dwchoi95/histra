"""Blinded expert evaluation kit (paper §IV, expert study): HISTRA vs HISTRA with H = {} (histra_nohist).
Samples trajectories where both repairers pass, the intent skeleton is non-empty, and the two patches differ
(AST-normalized); PER pairs per problem (stratified, fixed seed) plus CALIB calibration pairs from the rest.
Writes OUT/rating.html and OUT/calibration.html (self-contained rating pages in Korean; raters see the problem, the
buggy program, and two unified diffs in random A/B order) and OUT/key.csv (hidden mapping). Each pair has two stages:
(1) P-Feedback on the problem, the buggy program, and the two diffs only, as an instructor would see a submission;
(2) once (1) is answered, the student's earlier submissions appear (the first one and the diffs between consecutive
ones; never the skeleton) and the rater answers P-Intent. Changing (1) after the history appeared is recorded.
Usage: python expert_kit.py [EVAL_DIR] [OUT_DIR]     env: PER=7 CALIB=10 SEED=2027 SKIP=<pid,...>"""
import ast, csv, difflib, html, json, os, random, re, sys

EVAL = sys.argv[1] if len(sys.argv) > 1 else "results/eval"
OUT = sys.argv[2] if len(sys.argv) > 2 else "results/expert_eval"
PER, CALIB, SEED = int(os.environ.get("PER", 7)), int(os.environ.get("CALIB", 10)), int(os.environ.get("SEED", 2027))
SKIP = set(filter(None, os.environ.get("SKIP", "").split(",")))
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
A_NAME, B_NAME = "histra_min", "histra_nohist"


def norm(src):
    try:
        return ast.unparse(ast.parse(src))
    except (SyntaxError, ValueError):
        return None


def load(name):
    return {(r["pid"], r["user"]): r for r in map(json.loads, open(f"{EVAL}/{name}.jsonl"))}


def empty_skeleton():
    """Trajectories whose intent skeleton is empty (depends on Sketch only; read from any .ret file)."""
    for d in (EVAL, "results/eval_pre_k1"):
        p = f"{d}/{A_NAME}.ret.jsonl"
        if os.path.exists(p):
            return {(r["pid"], r["user"]) for r in map(json.loads, open(p)) if r and r.get("ret_oracle") is None}
    return set()


def problem_text(pid):
    s = open(f"{DATA}/{pid}/problem.html", encoding="utf-8").read()
    s = re.sub(r"<(br|/p|/li|/h\d|/pre|/div)[^>]*>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n\n", s)).strip()


def udiff(a, b, n=2):
    return "\n".join(difflib.unified_diff(a.splitlines(), b.splitlines(), "before", "after", n=n, lineterm=""))


def full_diff(a, b):
    """The whole patched program with every line of a and b: a context window would hide unchanged lines (e.g., a
    final print) for one patch but not the other, depending on where each one changes the code."""
    return "\n".join(l for l in udiff(a, b, 10 ** 6).splitlines() if not l.startswith("@@"))


def main():
    A, B, empty = load(A_NAME), load(B_NAME), empty_skeleton()
    pool = {}
    for k in sorted(A):
        if k[0] in SKIP or k in empty or k not in B or A[k]["patch"] is None or B[k]["patch"] is None:
            continue
        a, b, buggy = norm(A[k]["patch"]), norm(B[k]["patch"]), norm(A[k]["was"][-1])
        if a and b and buggy and a != b:
            pool.setdefault(k[0], []).append((k, buggy, a, b, [norm(w) or w for w in A[k]["was"][:-1]]))
    rnd = random.Random(SEED)
    main_items, rest = [], []
    for pid in sorted(pool):
        xs = pool[pid][:]
        rnd.shuffle(xs)
        main_items += [(pid, x) for x in xs[:PER]]
        rest += [(pid, x) for x in xs[PER:]]
    calib = rnd.sample(rest, min(CALIB, len(rest)))
    os.makedirs(OUT, exist_ok=True)
    key = []
    for label, items in (("rating", main_items), ("calibration", calib)):
        rows, groups = [], {}
        for pid, x in items:
            groups.setdefault(pid, []).append(x)
        n = 0
        for pid in sorted(groups):                          # grouped by problem, shuffled within the group
            xs = groups[pid]
            rnd.shuffle(xs)
            for k, buggy, a, b, hist in xs:
                n += 1
                iid = f"{'C' if label == 'calibration' else 'Q'}{n:03d}"
                swap = rnd.random() < 0.5                    # A/B position decided per item
                left, right = (b, a) if swap else (a, b)
                key.append(dict(item=iid, set=label, pid=k[0], user=k[1], A=B_NAME if swap else A_NAME, B=A_NAME if swap else B_NAME))
                steps = hist + [buggy]                       # earlier submissions, then the buggy one
                rows.append(dict(item=iid, pid=pid, buggy=buggy, diffA=full_diff(buggy, left), diffB=full_diff(buggy, right),
                                 first=steps[0], hist=[udiff(x, y, 1) for x, y in zip(steps, steps[1:])]))
        problems = {pid: problem_text(pid) for pid in groups}
        page = TEMPLATE.replace("__DATA__", json.dumps(dict(set=label, items=rows, problems=problems)).replace("</", "<\\/"))
        open(f"{OUT}/{label}.html", "w", encoding="utf-8").write(page)
    with open(f"{OUT}/key.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "set", "pid", "user", "A", "B"])
        w.writeheader(); w.writerows(key)
    print(f"pool: {sum(map(len, pool.values()))} differing pairs over {len(pool)} problems "
          f"(min per problem {min(map(len, pool.values()))}) | rating {len(main_items)} | calibration {len(calib)} -> {OUT}/")


TEMPLATE = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Patch Rating</title>
<style>
:root{--bg:#fff;--fg:#1d1d1f;--mut:#666;--line:#d9d9de;--add:#e6ffec;--addfg:#116329;--del:#ffebe9;--delfg:#82071e;--card:#f7f7f8;--acc:#0b57d0;--accfg:#fff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17181a;--fg:#e8e8ea;--mut:#a0a0a8;--line:#3a3b40;--add:#12301c;--addfg:#7ee2a0;--del:#3a1518;--delfg:#ff9aa2;--card:#202124;--acc:#8ab4f8;--accfg:#111}}
:root[data-theme="dark"]{--bg:#17181a;--fg:#e8e8ea;--mut:#a0a0a8;--line:#3a3b40;--add:#12301c;--addfg:#7ee2a0;--del:#3a1518;--delfg:#ff9aa2;--card:#202124;--acc:#8ab4f8;--accfg:#111}
body{background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;margin:0 auto;max-width:1200px;padding:16px}
h1{font-size:20px;margin:0 0 6px} h2{font-size:17px;margin:28px 0 4px} .mut{color:var(--mut)}
.guide{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:8px 0}
.guide ol{margin:4px 0;padding-left:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:14px 0}
.card.complete{border-color:var(--addfg)}
pre{font:13px/1.45 ui-monospace,Menlo,monospace;overflow-x:auto;margin:6px 0;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--bg)}
.add{background:var(--add);color:var(--addfg);display:block}.del{background:var(--del);color:var(--delfg);display:block}.hunk{color:var(--mut);display:block}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px} @media (max-width:800px){.cols{grid-template-columns:1fr}}
.qrow{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:8px 0}
.qtext{flex:1 1 320px;font-weight:600}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.seg input{position:absolute;opacity:0;pointer-events:none}
.seg label{padding:6px 16px;cursor:pointer;border-left:1px solid var(--line);user-select:none;min-width:44px;text-align:center}
.seg label:first-of-type{border-left:none}
.seg input:checked+label{background:var(--acc);color:var(--accfg)}
.seg input:focus-visible+label{outline:2px solid var(--acc);outline-offset:-2px}
.bar{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:8px 0;z-index:1;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
button{font:inherit;padding:6px 12px;border-radius:6px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
.done{color:var(--addfg);font-weight:600}
input[type=text]{font:inherit;box-sizing:border-box;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px;padding:4px 6px}
.memo{width:100%} .stage{border-top:1px dashed var(--line);margin-top:10px;padding-top:6px}
.stage h4{margin:4px 0;font-size:14px} .locked{opacity:.45} .seg input:disabled+label{cursor:not-allowed}
.hist pre{margin:4px 0 10px} .hist .step{font-size:13px;color:var(--mut)}
</style></head><body>
<h1>수정 패치 비교 평가 <span class="mut" id="setname"></span></h1>
<div class="guide">
<ol>
<li>각 항목은 한 학생의 <b>마지막 틀린 제출</b>과, 이를 고친 <b>두 패치 A, B</b>입니다. 각 패치는 프로그램 전체를 보여 주며, 빨간 줄은 지운 줄, 초록 줄은 추가한 줄입니다. 두 패치 모두 모든 테스트를 통과합니다. 패치의 출처는 숨겨져 있고 A/B 순서는 무작위입니다.</li>
<li><b>① 피드백</b>: 이 정보만 보고, 이 학생에게 피드백으로 보여 줄 패치를 고릅니다. 테스트는 통과하지만 틀려 보이거나 혼란을 줄 패치는 고르지 않습니다.</li>
<li><b>② 학생의 의도</b>: ①에 답하면 이 학생의 <b>이전 제출</b>이 나타납니다. 이전 제출에서 학생이 무엇을 유지하고 무엇을 계속 고쳤는지 보고, 학생이 하려던 풀이를 더 잘 살린 패치를 고릅니다. ①의 답은 이전 제출을 보기 전의 판단으로 두고 바꾸지 않습니다.</li>
<li>두 질문 모두 <b>A / 비슷함 / B</b> 중 하나로 답합니다. 두 패치가 실질적으로 같거나 우열을 가리기 어려우면 "비슷함"을 고릅니다. 두 질문의 답은 같을 수도 있고 다를 수도 있습니다.</li>
<li>답은 이 브라우저에 자동 저장됩니다. 나눠서 하셔도 됩니다. 다 마치면 <b>CSV 내보내기</b>를 눌러 파일을 보내 주세요.</li>
</ol></div>
<div class="bar"><label>평가자 ID <input id="rater" type="text" style="width:110px"></label>
<span id="progress"></span><button id="next">다음 미완료 항목</button><button id="export">CSV 내보내기</button></div>
<div id="items"></div>
<script>
const D = __DATA__;
document.getElementById('setname').textContent = '(' + (D.set === 'calibration' ? '연습' : '본 평가') + ', ' + D.items.length + '쌍)';
const KEY = 'patchrating3-' + D.set;
let S = {}; try { S = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const diffHtml = d => d.split('\n').map(l => l.startsWith('+++') || l.startsWith('---') ? '' :
  l.startsWith('@@') ? '<span class="hunk">⋯</span>' : l.startsWith('+') ? '<span class="add">'+esc(l)+'</span>' :
  l.startsWith('-') ? '<span class="del">'+esc(l)+'</span>' : esc(l)+'\n').join('');
const numbered = s => s.split('\n').map((l,i) => String(i+1).padStart(3)+'  '+esc(l)).join('\n');
const QS = [['P_Feedback', '이 학생에게 피드백으로 보여 준다면 어느 패치를 고르겠습니까?'],
            ['P_Intent', '이전 제출까지 보면, 학생이 하려던 풀이를 더 잘 살린 패치는?']];
const OPTS = [['A','A'], ['About the same','비슷함'], ['B','B']];
const seg = (id, q, off) => '<span class="seg" role="radiogroup">' + OPTS.map(([v, t], i) => {
  const rid = `${id}-${q}-${i}`, on = S[id] && S[id][q] === v ? 'checked' : '';
  return `<input type="radio" id="${rid}" name="${id}|${q}" value="${v}" ${on} ${off ? 'disabled' : ''}><label for="${rid}">${t}</label>`; }).join('') + '</span>';
const histHtml = it => `<div class="step">1번째 제출</div><pre>${numbered(it.first)}</pre>` + it.hist.map((d, i) =>
  `<div class="step">${i + 1}번째 → ${i + 2 === it.hist.length + 1 ? '마지막(위 코드)' : (i + 2) + '번째'} 제출에서 바뀐 부분</div>` +
  (d ? `<pre>${diffHtml(d)}</pre>` : '<pre class="mut">(바뀐 부분 없음)</pre>')).join('') +
  '<div class="step">이전 제출은 바뀐 줄 주변만 보여 주며, ⋯는 생략된 줄입니다.</div>';
const revealed = id => !!(S[id] && S[id].P_Feedback);
let html = '', last = null;
for (const it of D.items) {
  if (it.pid !== last) { html += `<h2>${it.pid}</h2><details><summary>문제 설명 보기</summary><pre style="white-space:pre-wrap">${esc(D.problems[it.pid])}</pre></details>`; last = it.pid; }
  html += `<div class="card" id="${it.item}"><b>${it.item}</b> <span id="st-${it.item}"></span>
  <details open><summary>학생의 틀린 제출</summary><pre>${numbered(it.buggy)}</pre></details>
  <div class="cols"><div><b>패치 A</b><pre>${diffHtml(it.diffA)}</pre></div><div><b>패치 B</b><pre>${diffHtml(it.diffB)}</pre></div></div>
  <div class="stage"><h4>① 피드백</h4><div class="qrow"><span class="qtext">${QS[0][1]}</span>${seg(it.item, QS[0][0])}</div></div>
  <div class="stage" id="s2-${it.item}"><h4>② 학생의 의도 <span class="mut" id="lk-${it.item}"></span></h4>
   <div class="hist" id="h-${it.item}"></div>
   <div class="qrow"><span class="qtext">${QS[1][1]}</span><span id="q2-${it.item}"></span></div></div>
  <div class="qrow"><input class="memo" type="text" placeholder="메모 (선택)" data-item="${it.item}" value="${esc((S[it.item]||{}).comment||'')}"></div></div>`;
}
document.getElementById('items').innerHTML = html;
const ITEM = Object.fromEntries(D.items.map(it => [it.item, it]));
const stage2 = id => { const open = revealed(id);
  document.getElementById('s2-'+id).classList.toggle('locked', !open);
  document.getElementById('lk-'+id).textContent = open ? '' : '(①에 답하면 이전 제출이 나타납니다)';
  const h = document.getElementById('h-'+id); if (open && !h.innerHTML) h.innerHTML = histHtml(ITEM[id]);
  document.getElementById('q2-'+id).innerHTML = seg(id, 'P_Intent', !open); };
D.items.forEach(it => stage2(it.item));
const FIELDS = QS.map(([q]) => q);
const complete = id => FIELDS.every(f => S[id] && S[id][f]);
const refresh = () => { let n = 0; for (const it of D.items) { const ok = complete(it.item); n += ok;
  document.getElementById('st-'+it.item).innerHTML = ok ? '<span class="done">완료</span>' : '';
  document.getElementById(it.item).classList.toggle('complete', ok); }
  document.getElementById('progress').textContent = `${n} / ${D.items.length} 완료`; };
document.addEventListener('change', e => { const t = e.target;
  if (t.type === 'radio') { const [id, q] = t.name.split('|'); const r = (S[id] = S[id] || {});
    if (q === 'P_Feedback' && r.P_Feedback && r.P_Feedback !== t.value && r.P_Intent) r.fb_changed = 1;   // changed after seeing the history
    r[q] = t.value; if (q === 'P_Feedback') stage2(id); }
  if (t.type === 'text' && t.dataset.item) (S[t.dataset.item] = S[t.dataset.item] || {}).comment = t.value;
  if (t.id === 'rater') S._rater = t.value; save(); refresh(); });
document.getElementById('rater').value = S._rater || '';
document.getElementById('next').onclick = () => { const it = D.items.find(x => !complete(x.item));
  if (it) document.getElementById(it.item).scrollIntoView({behavior: 'smooth', block: 'start'}); };
document.getElementById('export').onclick = () => {
  if (!(S._rater || '').trim()) { alert('평가자 ID를 먼저 입력해 주세요.'); document.getElementById('rater').focus(); return; }
  const rows = [['rater','item','P_Intent','P_Feedback','fb_changed','comment']];
  for (const it of D.items) { const r = S[it.item] || {};
    rows.push([S._rater||'', it.item, r.P_Intent||'', r.P_Feedback||'', r.fb_changed ? 1 : 0, r.comment||'']); }
  const csv = '﻿' + rows.map(r => r.map(x => '"'+String(x).replace(/"/g,'""')+'"').join(',')).join('\n');
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([csv], {type:'text/csv'}));
  a.download = `ratings_${D.set}_${S._rater||'rater'}.csv`; a.click(); };
refresh();
</script></body></html>
"""

if __name__ == "__main__":
    main()
