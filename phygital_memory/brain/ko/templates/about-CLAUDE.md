<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

이 폴더에는 {Name}님에 대한 핵심 사실이 있어요. 다른 모든 작업은 이 노트들을 기준으로 해요.

## 파일

| 파일 | 내용 | 분류 태그 |
|---|---|---|
| `나.md` | {Name}님이 어떤 사람인지, 어떻게 일하는지, 에이전트가 어떻게 일해 주길 원하는지 | `identity` |
| `살아온이야기.md` | {Name}님이 살아온 이야기 | `identity` |
| `목표.md` | 목표와 우선순위 | `goals` |
| `사업.md` | 사업 | `business` |
| `서비스.md` | 서비스, 제품, 제공하는 것 | `business` |
| `고객.md` | 누가 사는지, 어떻게 {Name}님을 찾아오는지 | `customers` |
| `고민.md` | 해결할 문제 | `customers` ({Name}님이 파는 게 없으면 `goals`) |
| `브랜드.md` | 목소리, 말투, 쓸 말과 피할 말 | `brand` |
| `도구.md` | 도구, 그리고 어떤 종류의 자료가 어디에 있는지 | `tools` |
| `경력.md` | 경력, 학력, 언론 보도, 수상 | `career` |

## 정보 블록(frontmatter)

여기 있는 모든 파일(이 파일 빼고)은 이렇게 시작해요:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "{Name}님이 어떤 사람이고, 에이전트가 어떻게 일해 주길 원하는지."
---
```

- `type`: 항상 `about`.
- `status`: `active`, 또는 어떤 사실이 낡은 걸 알게 되면 `outdated`.
- `updated`: 사실이 마지막으로 바뀐 날짜. 오타나 문장만 고쳤을 때는 바꾸지 않아요.
- `tags`: 먼저 `about`, 그다음 위 표에 있는 파일의 분류 태그, 그다음 파일이 다루는 주제 태그(영어, 소문자, 하이픈). 섹션을 더하거나 빼면 주제 태그도 업데이트해요.
- `description`: 이 파일에 무엇이 있는지 말하는 한 문장. 큰따옴표로 감싸고, 항상 마지막 줄에 써요.

## 규칙

- 이 파일들이 기준이에요. 내용을 다른 곳에 복사하지 말고 링크해요.
- "지금 상태 먼저" 형식(최상위 규칙 17): 맨 위에 지금의 사실, 그 아래에 날짜가 붙은 근거.
- {Name}님의 정확한 생년월일은 `나.md`에만 있어요. 절대 복사하거나 답장에서 말하지 마세요. 태어난 해는 괜찮아요.
- 새 주제가 생겨서 정말 필요할 때만 새 파일을 만들어요. 먼저 물어봐요(최상위 규칙 9).
- 전체 점검에서는, `목표.md`에 있는 목표 중 진행 중인 프로젝트가 없는 걸 짚어 줘요.
