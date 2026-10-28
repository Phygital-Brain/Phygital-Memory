<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

AI 代理使用的各個技能的筆記和偏好設定，還有大腦管家。

## 結構

```
技能/{skill-name}/
  {skill-name}.md 或 SKILL.md   這個技能做什麼
  notes.md                      {Name} 在這個技能上的語氣和偏好
  references/                   範例和比較長的資料
```

## 已安裝

| 技能 | 資料夾 | 做什麼 |
|---|---|---|
| 大腦管家 | `大腦管家/` | 每天自動整理，{Name} 要求時做健檢 |
| 晨間簡報 | `晨間簡報/` | 一份簡短的當日計畫，{Name} 要的時候給，或每個工作日自動給 |
| 匯入 | `匯入/` | 把其他應用程式的筆記搬進來，先給 {Name} 看過計畫並同意 |
| 會前準備 | `會前準備/` | 通話前根據大腦裡的筆記，給一份簡短的重點整理 |
| 思考工具 | `思考工具/` | 挑戰一個想法、找出規律、找出互相矛盾的筆記 |
| 已連結的應用程式 | `已連結的應用程式/` | 大腦會讀取哪些應用程式，以及相關規則 |
| No AI Slop | `no-ai-slop/` | 文字檢查：修改文字讓它讀起來像真人寫的，或標出 AI 的寫法（作者 Peter Yang，MIT License，絕不修改） |

## 規則

- 一個技能一個資料夾，用 kebab-case 命名。
- 加了新技能時，在上面的表格加一列。
- 要加技能或連結應用程式時，先看看 Phygital Brain 的推薦：透過 Phygital Brain 連接器查看 `suggested-skills/README.md` 和 `suggested-apps/README.md`，或在網路上打開 https://github.com/Phygital-Brain/phygital-brain/tree/main/skills 查看。如果在裡面，就照它的頁面做。{Name} 問「我的大腦還能加什麼？」、"what can I add to my brain?" 時，把兩份清單都列出來，適合 {Name} 工作的放前面，已經連結的應用程式和已經安裝的技能就不用列。
- 從別人那裡拿來的 `SKILL.md` 絕對不修改。想客製化一個技能，就在它的資料夾裡加一個 `筆記.md`。
- `大腦管家/每日整理.md` 由排程任務讀取。只有在要改變每天執行的內容時才改它，而且要保持單純：不放連結、不放提示框。
