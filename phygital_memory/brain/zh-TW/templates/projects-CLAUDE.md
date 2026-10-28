每個專案都是一個資料夾，隨著資訊進來慢慢長大。`README.md` 是唯一的入口。

## 分類

| 內容 | 放在 |
|---|---|
| 概要、進度、截止日期、下一步 | `專案/{name}/README.md` |
| {Name} 的工作筆記 | `專案/{name}/筆記/{topic}.md` |
| 研究 | `專案/{name}/研究/{topic}.md` |
| 需求說明、規格、要求 | `專案/{name}/需求說明/{name}.md` |
| 草稿、腳本、文字內容 | `專案/{name}/草稿/{name}.md` |
| 點子 | `專案/{name}/點子/{name}.md` |
| 回饋 | `專案/{name}/回饋/{name}.md` |
| 圖片和多媒體 | `專案/{name}/素材/` |
| 這個專案的舊資料 | `專案/{name}/封存/` |

資料夾名稱用小寫和連字號，前面不加編號（寫 `研究/`，不要寫 `01-Research/`）。如果這些都不合適，專案可以加自己的資料夾。

## README 的版面

1. 資訊區塊（見下方），要有 `description`。
2. `## 這是什麼`：一兩行，連到 [[目標]]。
3. `## 進度與下一步`：目前進行到哪裡、下一步是什麼。
4. `## 怎麼運作`：只有在有自動化的東西寫到這裡時才加（排程任務、腳本）。
5. `## 東西在哪裡`：有子資料夾之後才加。用一張小表格連到每個子資料夾。

## 資訊區塊（frontmatter）

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`：`project`（README，另外還有 `created`、`updated` 和 `description`）、`notes`、`research`、`brief`、`draft`、`idea`、`feedback`、`plan`。
- `status`：`active`、`paused` 或 `done`。README 的狀態就是專案的狀態。
- `project`：專案資料夾的名稱。
- `tags`：先寫專案，再寫類型。

## 規則

- 新專案只要一個 `README.md` 就好。等到有內容需要時才建立子資料夾，並從 README 連過去。
- README 就是目錄。不要在裡面重複子資料夾的內容。
- 專案裡面不放 `CLAUDE.md`。只適用單一專案的規則，寫在下面的「各專案的規則」。
- 每一則相關筆記的資訊區塊都要有 `project:`。
- 專案完成後，只有在 {Name} 說可以時，才搬到 `紀錄/封存/{name}/`。
- 每個專案都應該為 [[目標]] 裡的某個目標服務。健檢時，把沒有專案的目標和沒有目標的專案標出來。

## 各專案的規則

<!-- 只適用單一專案的規則。某個專案需要自己的規則時，加一行：「**Project-Name**：規則內容。」 -->
