隨著時間累積下來的知識：決定、研究、申請和封存。

## 分類

| 內容 | 放在 |
|---|---|
| 附上理由的決定，或是對外部事物（應用程式、網站、課程、競爭對手）的研究 | `決定/YYYY-MM-DD-{title}.md` |
| 研究（市場、趨勢、各種選項） | `研究/{topic}.md` |
| 申請：工作、補助、獎項、公開徵件（第一次用到時才建立） | `申請/{name}/` |
| 競爭對手的資料（第一次用到時才建立） | `競爭對手/{name}.md` |
| 金錢：發票、稅務、付款。私人 | `財務/` |
| 封存的決定 | `封存/決定/` |
| 已完成或過時的研究 | `封存/研究/` |
| 已完成的專案 | `封存/{name}/` |
| 會議紀錄 | 如果會議做出了決定，放 `決定/`；不然就放當天的 `日記/` 日記。只有會議紀錄很多時，才建議開一個會議資料夾。 |

## 資訊區塊（frontmatter）

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`：`decision`、`research`、`application`、`competitor`。
- `date`：寫這則筆記的日期。
- `status`：決定和申請請看下面。其他的：`active` 或 `closed`。
- `tags`：先寫類型，再寫主題。
- 可以加：`project`、`deadline`、`description`（一句話，用雙引號括起來，放最後一行）。

## 決定筆記

一定要寫出原因：有誰參與、起因是什麼、做了什麼取捨。決定本身用 `> [!important]`，已知的風險用 `> [!warning]`。

決定筆記在 `date:` 後面還要加上 `updated:`。`date` 是建立的日期，`updated` 是最後一次檢視或修改的日期。

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`：`open`（還在決定或還在進行）、`waiting`（在等別人）、`paused`、`closed`。
- `updated` 超過 30 天的決定需要重新檢視。大腦管家會一直標出來，直到 {Name} 選擇保留、結案或封存（每一種都會把 `updated` 改成當天）。
- 只有在 {Name} 說可以時，決定才會移到 `封存/決定/`。

## 申請

一個申請一個資料夾：`申請/{name}/`，裡面放一個 `README.md`，寫截止日期、連結、狀態和送出了什麼。其他檔案（答案、個人陳述）放在旁邊。

- `status`：`draft`、`submitted`、`accepted`、`rejected` 或 `withdrawn`。
- 答案用 Markdown 保存。大型 PDF 和簡報檔留在筆記庫外面：在筆記裡寫摘要就好。

## 規則

- 研究預設保持中立（主規則第 23 條）。
- 被新研究取代的舊研究，移到 `封存/研究/`，不要刪掉。
- `財務/` 是私人的，已列在 `.claudeignore` 裡。只有 {Name} 指名要某個檔案時才打開（主規則第 8 條）。
