프로젝트 하나가 폴더 하나이고, 정보가 들어올수록 자라요. `README.md`가 유일한 입구예요.

## 분류

| 내용 | 저장할 곳 |
|---|---|
| 개요, 상태, 마감일, 다음 단계 | `프로젝트/{name}/README.md` |
| {Name}님의 작업 메모 | `프로젝트/{name}/메모/{topic}.md` |
| 리서치 | `프로젝트/{name}/리서치/{topic}.md` |
| 의뢰서, 사양, 요구 사항 | `프로젝트/{name}/의뢰서/{name}.md` |
| 초안, 대본, 글 | `프로젝트/{name}/초안/{name}.md` |
| 아이디어 | `프로젝트/{name}/아이디어/{name}.md` |
| 피드백 | `프로젝트/{name}/피드백/{name}.md` |
| 이미지와 미디어 | `프로젝트/{name}/미디어/` |
| 이 프로젝트의 오래된 자료 | `프로젝트/{name}/보관함/` |

폴더 이름 앞에는 번호를 붙이지 않아요(`리서치/`처럼 쓰고, `01-Research/`처럼 쓰지 않아요). 영어 이름이면 소문자로 쓰고, 단어 사이는 하이픈으로 이어요. 이 중에 맞는 게 없으면 프로젝트에 맞는 폴더를 따로 만들어도 돼요.

## README 구성

1. 정보 블록(아래 참고), `description` 포함.
2. `## 개요`: 한두 줄, [[목표]]로 링크.
3. `## 현재 상황과 다음 단계`: 지금 어디까지 왔는지, 다음 단계.
4. `## 자동으로 돌아가는 것`: 여기에 자동으로 뭔가 쓰는 게 있을 때만(예약 작업, 스크립트).
5. `## 파일 위치`: 하위 폴더가 생긴 뒤에만. 각 폴더로 가는 링크를 담은 작은 표.

## 정보 블록(frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project`(README. `created`, `updated`, `description`도 있어요), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused`, `done`. README의 상태가 곧 프로젝트의 상태예요.
- `project`: 프로젝트 폴더 이름.
- `tags`: 먼저 프로젝트, 그다음 종류.

## 규칙

- 새 프로젝트는 `README.md` 하나로 시작해요. 하위 폴더는 그게 필요한 내용이 들어올 때만 만들고, README에서 링크해요.
- README는 목차예요. 하위 폴더 내용을 README에 되풀이하지 않아요.
- 프로젝트 안에는 `CLAUDE.md`를 두지 않아요. 한 프로젝트만의 규칙은 아래 "프로젝트별 규칙"에 써요.
- 관련된 모든 노트의 정보 블록에 `project:`를 넣어요.
- 끝난 프로젝트는 {Name}님이 말할 때만 `기록/보관함/{name}/`로 옮겨요.
- 모든 프로젝트는 [[목표]]에 있는 목표 하나에 도움이 되어야 해요. 전체 점검에서는 프로젝트가 없는 목표와 목표가 없는 프로젝트를 짚어 줘요.

## 프로젝트별 규칙

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
