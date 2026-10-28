<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `客戶/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

所有跟 {Name} 一起工作的人：一個人或一個組織一則筆記。

## 子資料夾

| 資料夾 | 放誰 |
|---|---|
| `客戶/` | {Name} 接案服務的人和公司 |
| `合作夥伴/` | 創作上的夥伴，互相交流，不涉及金錢 |
| `團隊/` | 跟 {Name} 一起工作或替 {Name} 工作的人（接案者、助理） |
| `合作單位/` | {Name} 想一起打開知名度的組織（媒體、場地、平台） |

## 新的潛在客戶放哪裡

- 第一次接觸，還沒有真正的需求：在 `客戶/_潛在客戶.md`（第一次用到時才建立）的 `## 新的` 下面寫一行。
- 回覆說「以後再說」：在 `客戶/_潛在客戶.md` 的 `## 保持聯繫` 下面寫一行。
- 有真正的需求、通話或正在報價：建立一則客戶筆記 `客戶/{client-name}.md`，設為 `status: prospect`。

潛在客戶往前進一步時，就移到下一個位置，並從原本的位置刪掉。

## 資訊區塊（frontmatter）

這裡的每一則筆記（`CLAUDE.md` 檔案和 `_潛在客戶.md` 除外）開頭都是：

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "用一句白話說明對方是誰，以及跟 {Name} 的關係。"
---
```

- `type`：`client`、`collaborator`、`team` 或 `partner`。
- `status`：`active`（最近 12 個月內有合作或聯絡）、`prospect`（在洽談中，還沒合作過）、`dormant`（12 個月以上沒聯絡）、`closed`（已經徹底結束）。
- `last-contact`：最近一次真正聯絡或合作的月份，`YYYY-MM`。不知道就留空。
- `tags`：先寫 `relationship`，再寫類型，接著是 2 到 5 個主題標籤（產業、國家、工作類型），英文、小寫、用連字號。
- `description`：一句話，用雙引號括起來。一定放在最後一行。
- 可以加：`aliases`（對方的其他稱呼）、`project`（目前的專案）。

## 規則

- **不要重複**。建立筆記之前，先搜尋這個名字和它的各種寫法（重音符號、空格、簡稱、中英文名、品牌名和公司名）。如果已經有筆記，就用那一則，並把新的寫法加進 `aliases`。同一個人或同一家公司絕對不要有第二則筆記。
- **「最新現況在上、依據在下」的格式**（主規則第 17 條）：最上面寫對方是誰和目前的狀況，下面是附日期的歷史。
- **保持最新**。{Name} 跟某人有真正的聯絡時（一封信、一通電話、交付了工作），把 `last-contact` 改成這個月；如果 `status` 有變，也一起改。
- **公司裡的聯絡窗口**（經紀人、經理、編輯）寫成公司筆記裡的純文字，絕對不寫成 `[[links]]`，也不另外建筆記。要在別的地方提到他們，就連到公司：`[[Company Name|Contact Name]]`。
- **私人資料**（電話、電子郵件、住址）只放在那個人或那家公司的筆記裡。絕對不要複製到日記或其他筆記。
- 從專案和日記用 `[[wikilinks]]` 連到這些人。
- 只有出現新的關係類型時，才建立新的子資料夾。要先問。
