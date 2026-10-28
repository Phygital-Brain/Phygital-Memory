<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

{Name} 的日記。一天一個檔案：`YYYY-MM-DD.md`。待辦事項放在 `待辦事項.md`。

## 資訊區塊（frontmatter）

每一篇日記開頭都是這個區塊，沒有例外。

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

- `type`：一律是 `daily`。
- `date`：這篇日記的日期，`YYYY-MM-DD`。
- `day`：星期幾，用英文寫（Monday、Tuesday……）。
- `week`：ISO 週數，`WNN`。
- `month`：月份，用英文寫（January、February……）。
- `status`：當天還沒結束時是 `active`，過了 2 天以上就是 `completed`。
- `tags`：一定有 `daily`，再從下面這份固定清單裡，挑出那天有發生的事。絕對不要自己發明其他標籤。
  - `problem`：有東西壞掉或出了問題
  - `clients`：客戶的工作或跟客戶聯絡
  - `meeting`：通話或開會
  - `money`：發票、付款、稅務、投資
  - `research`：做了研究或有新發現
  - `decision`：{Name} 做了某個決定
  - `travel`：{Name} 在旅行
  - `personal`：健康、生活，任何工作以外的事

## 規則

- 日期依照主規則第 30 條（先看電腦的時區，沒有再用 {Time zone}）。
- 建立日記的人（你的 AI 代理或排程任務）要先寫資訊區塊。沒有資訊區塊的日記，下次編輯時在最上面補上。
- 不要放 `# YYYY-MM-DD` 這種標題。檔名就是標題。
- 日記記的是當天的最新狀態：一天一份整齊的文件，各段落直接就地更新，絕對不要一筆一筆重複往下堆。
- 工作紀錄：粗體標題加上 1 到 2 句話，人和專案寫成 `[[wikilinks]]`，細節寫在連結的筆記裡。
- 今天的日記只寫今天的事。之前留下的待辦事項放到 `待辦事項.md`。絕對不要一天一天往下抄。
- 建立今天的日記時，看一下 2、3、4 天前的日記。還是 `status: active` 的，改成 `completed`，再依那天明顯發生的事，從固定清單加上標籤。不要再往前看。

## tasks.md

不屬於任何專案的待辦事項。專案的待辦事項寫在該專案的 README 裡（「進度與下一步」）。第一次用到時才建立：

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## 待辦

- [ ] 2026-10-13：把發票寄給 [[安娜]]

## 完成

- [x] 2026-10-12：預約牙醫（2026-10-13 完成）
```

- 最新的待辦事項放最上面，附上加入的日期。
- 事情做完時打勾，加上完成的日期，再移到 `## 完成`。
- 完成超過 30 天的事項可以刪掉（要先問，主規則第 9 條）。
