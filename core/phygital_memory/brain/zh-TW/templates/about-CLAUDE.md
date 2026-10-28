<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

這個資料夾放的是關於 {Name} 的核心事實。其他所有工作都以這裡的筆記為準。

## 檔案

| 檔案 | 用途 | 分類標籤 |
|---|---|---|
| `我.md` | {Name} 是誰、怎麼做事，以及希望 AI 代理怎麼做事 | `identity` |
| `人生故事.md` | {Name} 的人生故事 | `identity` |
| `目標.md` | 目標和優先順序 | `goals` |
| `事業.md` | 事業 | `business` |
| `服務.md` | 服務、產品、方案 | `business` |
| `客群.md` | 誰會買，以及他們怎麼找到 {Name} | `customers` |
| `痛點.md` | 要解決的問題 | `customers`（如果 {Name} 沒有在賣東西，就用 `goals`） |
| `品牌.md` | 語氣、口吻、要用和要避開的字 | `brand` |
| `工具.md` | 工具，以及每一類東西放在哪裡 | `tools` |
| `履歷.md` | 工作經歷、學歷、媒體報導、得獎紀錄 | `career` |

## 資訊區塊（frontmatter）

這裡的每個檔案（這個檔案除外）開頭都是：

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "{Name} 是誰，以及希望 AI 代理怎麼做事。"
---
```

- `type`：一律是 `about`。
- `status`：`active`；如果知道某個事實已經過時，就用 `outdated`。
- `updated`：事實最後一次改變的日期。只修錯字或調整文字時不用改。
- `tags`：先寫 `about`，再寫上表裡這個檔案的分類標籤，接著是說明檔案內容的主題標籤（英文、小寫、用連字號）。新增或刪除段落時，要一併更新主題標籤。
- `description`：一句話，用雙引號括起來，說明這個檔案放什麼。一定放在最後一行。

## 規則

- 這些檔案是唯一的依據。不要把內容複製到別的地方，改用連結。
- 「最新現況在上、依據在下」的格式（主規則第 17 條）：最上面寫目前的事實，下面是附日期的依據。
- {Name} 完整的出生日期只放在 `我.md`。絕對不要複製，也不要在回覆裡提到。只寫出生年份可以。
- 只有出現新主題、真的需要時，才建立新檔案。要先問（主規則第 9 條）。
- 健檢時，把 `目標.md` 裡沒有任何進行中專案的目標標出來。
