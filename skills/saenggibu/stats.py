#!/usr/bin/env python3
"""클로드 코드 대화 기록(~/.claude/projects)에서 내가 직접 친 메시지만 모아 생활기록부용 숫자와 증거를 뽑는다.
아무것도 밖으로 보내지 않는다. 결과는 JSON으로 표준출력."""
import json, re, sys, collections
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"
interrupts = 0  # 내가 Esc로 클로드를 중간에 끊은 횟수
PATTERNS = {
    "부정": r"^(아니|아냐|ㄴㄴ|노노)|아니\s*그게|그게 아니",
    "재시도": r"다시|또\s|한\s?번\s?더",
    "재촉": r"ㄱㄱ|빨리|얼른|ㅃㄹ|고고",
    "웃음": r"ㅋㅋ|ㅎㅎ",
    "짜증": r"ㅡㅡ|;;|왜\s?자꾸|왜\s?안|하\.\.|미친",
    "칭찬": r"좋아|굿|최고|잘했|완벽|오\s?좋",
    "부탁": r"제발|부탁",
}


def human_messages():
    global interrupts
    for f in ROOT.glob("*/*.jsonl"):
        try:
            lines = f.open(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in lines:
            if '"type":"user"' not in line.replace(" ", ""):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("isSidechain") or d.get("isMeta"):
                continue
            if "[Request interrupted by user" in line:
                interrupts += 1
                continue
            # 사람이 직접 친 메시지만: 데스크톱 앱은 origin.kind == "human",
            # origin 표시가 없는 예전 터미널 기록은 entrypoint == "cli" 이고 자동(sdk/system) 입력이 아닌 것.
            origin = (d.get("origin") or {}).get("kind")
            if origin != "human" and not (origin is None and d.get("entrypoint") == "cli"
                                          and d.get("promptSource") not in ("sdk", "system")):
                continue
            c = (d.get("message") or {}).get("content")
            if isinstance(c, list):
                c = " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
            if not isinstance(c, str) or not c.strip() or c.lstrip().startswith(("<", "This session is being continued", "[Image")):
                continue
            try:
                t = datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")).astimezone()
            except (KeyError, ValueError):
                continue
            yield {"t": t, "text": c.strip(), "cwd": d.get("cwd") or "", "session": d.get("sessionId") or f.stem}


def project_name(cwd):
    # 워크트리(.../프로젝트/.claude/worktrees/이름)는 원래 프로젝트 이름으로 묶는다.
    return Path(cwd.split("/.claude/worktrees/")[0]).name


def main():
    msgs = sorted(human_messages(), key=lambda m: m["t"])
    if not msgs:
        print(json.dumps({"error": "대화 기록을 찾지 못했어요 (~/.claude/projects)"}, ensure_ascii=False))
        return
    hours = collections.Counter(m["t"].hour for m in msgs)
    days = collections.Counter(m["t"].date() for m in msgs)
    dawn = [m for m in msgs if 0 <= m["t"].hour < 5]
    projects = collections.Counter(project_name(m["cwd"]) for m in msgs if m["cwd"])
    polite = sum(1 for m in msgs if re.search(r"(요|니다|세요)[.?!~ ]*$", m["text"]))  # 문장 끝 존댓말
    typed = [m for m in msgs if len(m["text"]) <= 300]  # 붙여넣은 긴 글은 말버릇에서 뺀다
    words = collections.Counter(w for m in typed for w in re.findall(r"[가-힣]{2,6}", m["text"]))

    def quotes(rx, n=6):
        hit = [m for m in msgs if re.search(rx, m["text"]) and len(m["text"]) <= 120]
        step = max(1, len(hit) // n)
        return [{"when": m["t"].strftime("%Y-%m-%d %H:%M"), "text": m["text"]} for m in hit[::step][:n]], len(hit)

    habits = {}
    for name, rx in PATTERNS.items():
        q, count = quotes(rx)
        habits[name] = {"횟수": count, "예시": q}
    busiest = days.most_common(1)[0]
    latest = max(msgs, key=lambda m: (m["t"].hour + 19) % 24)  # 오전 5시를 하루 시작으로 보고 가장 늦은 시각
    shortest = sorted({m["text"] for m in msgs if len(m["text"]) <= 4}, key=len)[:10]
    out = {
        "기간": {"첫 기록": msgs[0]["t"].strftime("%Y-%m-%d"), "마지막": msgs[-1]["t"].strftime("%Y-%m-%d"), "활동한 날": len(days)},
        "내 메시지 수": len(msgs),
        "대화 수": len({m["session"] for m in msgs}),
        "프로젝트 수": len(projects),
        "가장 많이 한 프로젝트": projects.most_common(3),
        "시간대": {str(h): hours.get(h, 0) for h in range(24)},
        "새벽(0~5시) 비율%": round(100 * len(dawn) / len(msgs), 1),
        "새벽 메시지 예시": [{"when": m["t"].strftime("%Y-%m-%d %H:%M"), "text": m["text"][:120]} for m in dawn[-5:]],
        "가장 늦은 시각 메시지": {"when": latest["t"].strftime("%Y-%m-%d %H:%M"), "text": latest["text"][:120]},
        "가장 바빴던 날": {"날짜": str(busiest[0]), "메시지": busiest[1]},
        "존댓말 비율%": round(100 * polite / len(msgs), 1),
        "중간에 끊은 횟수": interrupts,
        "메시지 길이 중간값": sorted(len(m["text"]) for m in msgs)[len(msgs) // 2],
        "제일 짧은 지시들": shortest,
        "자주 쓴 단어": words.most_common(15),
        "말버릇": habits,
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
