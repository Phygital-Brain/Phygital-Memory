<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

{Name}님의 하루 일지예요. 하루에 파일 하나: `YYYY-MM-DD.md`. 아직 안 끝난 할 일은 `할일.md`에 있어요.

## 정보 블록(frontmatter)

모든 일지는 이 블록으로 시작해요. 예외는 없어요.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: 항상 `daily`.
- `date`: 일지의 날짜, `YYYY-MM-DD`.
- `day`: 요일, 영어로(Monday, Tuesday...).
- `week`: ISO 주 번호, `WNN`.
- `month`: 월, 영어로(January, February...).
- `status`: 그날이 진행 중이면 `active`, 2일 이상 지나면 `completed`.
- `tags`: 항상 `daily`, 그리고 아래 정해진 목록 중 그날 있었던 것. 다른 태그는 절대 새로 만들지 않아요.
  - `problem`: 뭔가 고장 났거나 잘못됐을 때
  - `clients`: 클라이언트 작업이나 클라이언트와의 연락
  - `meeting`: 통화나 미팅
  - `money`: 청구서, 입금, 세금, 투자
  - `research`: 리서치를 했거나 알게 된 것
  - `decision`: {Name}님이 뭔가 결정했을 때
  - `travel`: {Name}님이 여행 중일 때
  - `personal`: 건강, 생활, 일 말고 다른 모든 것

## 규칙

- 날짜는 최상위 규칙 30을 따라요(먼저 컴퓨터의 시간대, 그다음 {Time zone}).
- 일지를 만드는 쪽(에이전트든 예약 작업이든)이 정보 블록을 먼저 써요. 정보 블록이 없는 일지는 다음에 고칠 때 맨 위에 넣어요.
- `# YYYY-MM-DD` 같은 제목은 넣지 않아요. 파일 이름이 곧 제목이에요.
- 일지에는 그날의 지금 상태가 담겨요. 하루에 깔끔한 문서 하나, 섹션은 그 자리에서 업데이트하고, 같은 내용을 계속 쌓지 않아요.
- 작업 기록: 굵은 제목 하나와 문장 1~2개, 사람과 프로젝트는 `[[wikilinks]]`로, 자세한 내용은 링크한 노트에 써요.
- 오늘 일지에는 오늘 한 일만 써요. 지난날의 할 일은 `할일.md`로 가요. 절대 다음 날로 옮겨 적지 않아요.
- 오늘 일지를 만들 때, 2일 전, 3일 전, 4일 전 일지를 봐요. 아직 `status: active`인 게 있으면 `completed`로 바꾸고, 그날 분명히 있었던 일에 맞게 정해진 목록에서 태그를 붙여요. 그보다 더 전은 보지 않아요.

## tasks.md

프로젝트에 속하지 않은 할 일이에요. 프로젝트 할 일은 그 프로젝트의 README("현재 상황과 다음 단계")에 써요. 처음 필요할 때 만들어요:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## 할 일

- [ ] 2026-10-13: [[하은]]님에게 청구서 보내기

## 끝난 일

- [x] 2026-10-12: 치과 예약하기 (2026-10-13 완료)
```

- 새로 생긴 할 일은 맨 위에, 추가한 날짜와 함께 써요.
- 할 일을 끝내면 체크하고, 끝낸 날짜를 붙이고, `## 끝난 일`로 옮겨요.
- 30일보다 오래된 끝난 일은 지워도 돼요(먼저 물어봐요, 최상위 규칙 9).
