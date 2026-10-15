#!/usr/bin/env python3
"""content.json(클로드가 쓴 글 + 통계)을 학교생활기록부 양식 HTML 카드로 그린다. 사용: render.py content.json"""
import html, json, subprocess, sys
from pathlib import Path

c = json.load(open(sys.argv[1], encoding="utf-8"))
e = lambda s: html.escape(str(s))
out = Path.home() / "claude-saenggibu" / "생활기록부.html"
out.parent.mkdir(exist_ok=True)

rows_award = "".join(f"<li>{e(a)}</li>" for a in c["수상경력"])
rows_quote = "".join(
    f'<li><span class="when">{e(q["when"])}</span> “{e(q["text"])}” <span class="note">— {e(q["코멘트"])}</span></li>'
    for q in c["증거"])
page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>클로드 생활기록부</title>
<link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;800&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#e9e4d8;font-family:"Nanum Myeongjo","AppleMyungjo",serif;color:#222}}
.paper{{max-width:620px;margin:24px auto;background:#fffdf7;padding:28px 30px 96px;box-shadow:0 4px 18px rgba(0,0,0,.15);position:relative}}
h1{{text-align:center;font-size:26px;letter-spacing:6px;margin:0 0 4px}}
.school{{text-align:center;color:#666;font-size:13px;margin-bottom:18px}}
table{{width:100%;border-collapse:collapse;font-size:14px;margin-bottom:14px}}
th,td{{border:1px solid #555;padding:7px 9px;vertical-align:top}} th{{background:#f1ede2;width:118px;font-weight:800;text-align:center}}
ul{{margin:0;padding-left:18px}} li{{margin:3px 0}}
.when{{color:#888;font-size:12px}} .note{{color:#555;font-size:13px}}
.stamp{{position:absolute;right:34px;bottom:20px;width:86px;height:86px;border:3px solid #d33;border-radius:50%;color:#d33;
display:flex;align-items:center;justify-content:center;text-align:center;font-weight:800;font-size:15px;transform:rotate(-14deg);opacity:.85}}
.foot{{text-align:center;font-size:11px;color:#999;margin-top:22px}}
</style></head><body><div class="paper">
<h1>학교생활기록부</h1><div class="school">클로드고등학교 · {e(c["학년"])}</div>
<table>
<tr><th>성명</th><td>{e(c["이름"])}</td></tr>
<tr><th>출결상황</th><td>수업일수 {e(c["통계"]["활동한 날"])}일 · 새벽 등교(0~5시) {e(c["통계"]["새벽 비율"])}% · 조퇴(중간에 끊음) {e(c["통계"]["끊은 횟수"])}회<br>최장 야자: {e(c["통계"]["가장 늦은 시각"])}</td></tr>
<tr><th>수상경력</th><td><ul>{rows_award}</ul></td></tr>
<tr><th>창의적<br>체험활동</th><td>{e(c["창체"])}</td></tr>
<tr><th>세부능력 및<br>특기사항</th><td>{e(c["세특"])}</td></tr>
<tr><th>행동특성 및<br>종합의견</th><td>{e(c["종합의견"])}<ul style="margin-top:8px">{rows_quote}</ul></td></tr>
<tr><th>진로희망</th><td>{e(c["진로희망"])}</td></tr>
</table>
<div class="stamp">{e(c.get("도장", "참 잘<br>했어요")).replace("&lt;br&gt;", "<br>")}</div>
<div class="foot">내 클로드 대화 기록으로 만든 생활기록부 · github.com/hesong0222-dev/claude-saenggibu</div>
</div></body></html>"""
out.write_text(page, encoding="utf-8")
print(out)
subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(out)], check=False)
