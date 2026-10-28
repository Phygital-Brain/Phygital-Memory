<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `클라이언트/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

{Name}님이 함께 일하는 모든 사람과 단체예요. 사람이나 단체 하나에 노트 하나.

## 하위 폴더

| 폴더 | 들어가는 사람 |
|---|---|
| `클라이언트/` | {Name}님이 일을 해 주는 사람과 회사 |
| `협업자/` | 창작 파트너. 서로 주고받는 관계이고, 돈이 오가지 않아요 |
| `팀/` | {Name}님과 함께, 또는 {Name}님을 위해 일하는 사람(프리랜서, 어시스턴트) |
| `파트너/` | {Name}님이 이름을 알리려고 함께하는 단체(언론, 행사장, 플랫폼) |

## 새 잠재 고객은 어디로

- 첫 연락이지만 아직 구체적인 의뢰가 없을 때: `클라이언트/_잠재고객.md`(처음 필요할 때 만들어요)의 `## 새 문의` 아래에 한 줄.
- "나중에 생각해 볼게요"라는 답이 왔을 때: `클라이언트/_잠재고객.md`의 `## 계속 연락하기` 아래에 한 줄.
- 실제 의뢰, 통화, 견적이 진행 중일 때: `status: prospect`로 클라이언트 노트 `클라이언트/{client-name}.md`를 만들어요.

잠재 고객이 한 단계 올라가면, 다음 자리로 옮기고 이전 자리에서는 지워요.

## 정보 블록(frontmatter)

여기 있는 모든 노트(`CLAUDE.md` 파일과 `_잠재고객.md` 빼고)는 이렇게 시작해요:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "누구인지, 그리고 {Name}님과 어떤 관계인지 쉬운 한 문장으로."
---
```

- `type`: `client`, `collaborator`, `team`, `partner`.
- `status`: `active`(최근 12개월 안에 함께 일했거나 연락함), `prospect`(이야기 중이지만 함께 일한 적은 없음), `dormant`(12개월 넘게 연락 없음), `closed`(완전히 끝남).
- `last-contact`: 실제로 연락하거나 함께 일한 가장 최근 달, `YYYY-MM`. 모르면 비워 둬요.
- `tags`: 먼저 `relationship`, 그다음 종류, 그다음 주제 태그 2~5개(업계, 나라, 일의 종류). 영어, 소문자, 하이픈.
- `description`: 큰따옴표로 감싼 한 문장. 항상 마지막 줄에 써요.
- 선택 항목: `aliases`(그 사람이나 회사를 부르는 다른 이름), `project`(지금 진행 중인 프로젝트).

## 규칙

- **중복 금지.** 노트를 만들기 전에 이름과 그 변형(띄어쓰기, 줄임말, 영문 표기, 브랜드명과 회사명)을 검색해요. 노트가 있으면 그걸 쓰고, 새 표기를 `aliases`에 더해요. 같은 사람이나 회사에 두 번째 노트를 절대 만들지 않아요.
- **"지금 상태 먼저" 형식**(최상위 규칙 17): 맨 위에 누구인지와 지금 상태, 그 아래에 날짜가 붙은 기록.
- **최신으로 유지하기.** {Name}님이 누군가와 실제로 연락하면(이메일, 통화, 납품) `last-contact`를 이번 달로 바꾸고, `status`가 달라졌으면 그것도 바꿔요.
- **회사 담당자**(에이전트, 매니저, 편집자)는 회사 노트 안에 그냥 글자로 써요. 절대 `[[links]]`로 만들지 않고, 따로 노트도 만들지 않아요. 다른 곳에서 언급할 때는 회사를 링크해요: `[[Company Name|Contact Name]]`.
- **개인 정보**(전화번호, 이메일, 집 주소)는 그 사람이나 회사의 노트에만 있어요. 일지나 다른 노트에 절대 복사하지 않아요.
- 프로젝트와 일지에서 사람을 `[[wikilinks]]`로 링크해요.
- 새로운 종류의 관계가 생겼을 때만 새 하위 폴더를 만들어요. 먼저 물어봐요.
