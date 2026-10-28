<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

에이전트가 쓰는 스킬에 대한 메모와 취향, 그리고 정리 도우미가 있어요.

## 구조

```
스킬/{skill-name}/
  {skill-name}.md 또는 SKILL.md   스킬이 하는 일
  notes.md                        이 스킬에 대한 {Name}님의 목소리와 취향
  references/                     예시와 긴 자료
```

## 설치된 스킬

| 스킬 | 폴더 | 하는 일 |
|---|---|---|
| 정리 도우미 | `정리도우미/` | 매일 알아서 정리하고, {Name}님이 부탁하면 전체 점검 |
| 아침 브리핑 | `아침브리핑/` | 하루 계획을 짧게, 부탁할 때나 일하는 날마다 |
| 가져오기 | `가져오기/` | 다른 앱의 노트를 가져와요. {Name}님이 먼저 승인한 계획대로 |
| 미팅 준비 | `미팅준비/` | 통화 전에 브레인의 노트로 짧은 브리핑 |
| 생각 도구 | `생각도구/` | 아이디어 반박, 패턴 찾기, 서로 안 맞는 노트 찾기 |
| 연결된 앱 | `연결된앱/` | 브레인이 어떤 앱을 읽는지, 그 앱에 대한 규칙 |
| No AI Slop | `no-ai-slop/` | 글 점검: 글이 사람이 쓴 것처럼 들리게 고치거나, AI 패턴을 짚어 줘요(Peter Yang 작성, MIT License, 절대 수정하지 않아요) |

## 규칙

- 스킬 하나에 폴더 하나, 이름은 kebab-case로.
- 새 스킬이 추가되면 위 표에 한 줄 더해요.
- 스킬을 추가하거나 앱을 연결할 때는 먼저 Phygital Brain의 추천을 확인해요. Phygital Brain 커넥터로 `suggested-skills/README.md`와 `suggested-apps/README.md`를 보거나, 온라인에서 https://github.com/Phygital-Brain/phygital-brain/tree/main/skills 를 봐요. 거기에 있으면 그 페이지를 따라요. {Name}님이 "내 브레인에 뭘 추가할 수 있어?", 또는 "what can I add to my brain?"라고 물으면 두 목록을 모두 보여 줘요. {Name}님의 일에 맞는 것을 먼저 보여 주고, 이미 연결된 앱과 이미 설치된 스킬은 빼요.
- 다른 사람이 만든 `SKILL.md`는 절대 수정하지 않아요. 스킬을 내 방식에 맞추려면 그 폴더에 `메모.md`를 더해요.
- `정리도우미/매일정리.md`는 예약 작업이 읽어요. 매일 실행하는 내용을 바꿀 때만 고치고, 단순하게 유지해요: 링크도, 콜아웃도 없이.
