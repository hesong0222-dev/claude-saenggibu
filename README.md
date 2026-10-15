<p align="center"><img src="mascot.png" width="140"></p>

# 클로드 생활기록부 (claude-saenggibu)

내 클로드 코드 대화 기록을 읽고 **학교생활기록부**를 써주는 스킬.

- 출결: 새벽 0~5시에 클로드 부른 비율, 중간에 끊은(Esc) 횟수, 최장 야자 시각
- 수상경력: 내 숫자로 받는 상 3개 (예: "ㄱㄱ 명예홍보대사상 (재촉 88회)")
- 세부능력 및 특기사항: 말버릇. "아니"로 시작한 정정, "다시", "ㄱㄱ", 존댓말 비율…
- 행동특성 및 종합의견: 담임쌤 말투 총평 + **내가 실제로 보낸 메시지 3개를 증거로 인용**
- 진로희망: 한 줄

결과는 생활기록부 양식 카드로 브라우저에 열림. 캡처해서 올리면 끝.

## 설치

클로드 코드에 이 저장소 주소 붙여넣고 "이거 스킬로 설치해줘" 하면 됨. 직접 하려면:

```bash
git clone https://github.com/hesong0222-dev/claude-saenggibu /tmp/claude-saenggibu
mkdir -p ~/.claude/skills && cp -r /tmp/claude-saenggibu/skills/saenggibu ~/.claude/skills/
```

그다음 클로드 코드에서:

```
생활기록부 뽑아줘
```

## 개인정보

- 기록은 내 컴퓨터(`~/.claude/projects`)에서만 읽음. 어디로도 안 보냄
- 내가 직접 친 메시지만 셈 (예약 작업, 다른 세션이 보낸 메시지, 자동 입력은 뺌)
- 인용할 때 이름·메일·키 같은 건 고르지 않거나 ○○로 가림. 그래도 **올리기 전에 인용 한 번 확인**하세요
- 남과 비교하는 숫자(상위 몇 %)는 없음. 데이터 없이 지어내기 싫어서

## 숫자만 보고 싶으면

```bash
python3 ~/.claude/skills/saenggibu/stats.py
```

---

MIT · 만든 사람 [개발새발자](https://x.com/ComAsNas) · 재미용입니다. 진지하게 받아들이지 마세요
