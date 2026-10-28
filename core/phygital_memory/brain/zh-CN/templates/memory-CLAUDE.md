随着时间慢慢积累的知识：决定、调研、申请和归档。

## 归类

| 内容 | 放到 |
|---|---|
| 带理由的决定，或对外部事物的研究（应用、网站、课程、竞争对手） | `决定/YYYY-MM-DD-{title}.md` |
| 调研（市场、趋势、各种方案） | `调研/{topic}.md` |
| 申请：工作、资助、奖项、公开征集（第一次用到时创建） | `申请/{name}/` |
| 竞争对手档案（第一次用到时创建） | `竞争对手/{name}.md` |
| 钱：发票、税务、付款。私密 | `财务/` |
| 归档的决定 | `归档/决定/` |
| 已结束或过时的调研 | `归档/调研/` |
| 已完成的项目 | `归档/{name}/` |
| 会议记录 | 如果会上做了决定，就放 `决定/`，否则放当天的 `日记/` 日记。只有会议记录很多时，才建议建一个会议文件夹。 |

## 信息块（frontmatter）

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`：`decision`、`research`、`application`、`competitor`。
- `date`：写这篇笔记的日期。
- `status`：决定和申请见下文。其他的一律是 `active` 或 `closed`。
- `tags`：先写类型，再写主题。
- 可选：`project`、`deadline`、`description`（一句话，放在英文双引号里，放在最后一行）。

## 决定笔记

一定要写清原因：谁参与了，起因是什么，做了什么取舍。决定本身用 `> [!important]`，已知的风险用 `> [!warning]`。

决定笔记在 `date:` 后面还要紧跟一行 `updated:`。`date` 是创建的日期，`updated` 是最后一次复查或修改的日期。

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`：`open`（还在决定或推进中）、`waiting`（在等别人）、`paused`（暂停）、`closed`（已结束）。
- `updated` 超过 30 天的决定需要复查。大脑管家会一直标出它，直到 {Name} 选择保留、关闭或归档（每种做法都会把 `updated` 改成当天）。
- 只有 {Name} 说了，决定才移到 `归档/决定/`。

## 申请

每个申请一个文件夹：`申请/{name}/`，里面的 `README.md` 写截止日期、链接、状态和交了什么。其他文件（答题内容、个人陈述）放在旁边。

- `status`：`draft`、`submitted`、`accepted`、`rejected` 或 `withdrawn`。
- 答题内容用 Markdown 保存。大的 PDF 和幻灯片不放进大脑文件夹：在笔记里写个摘要。

## 规则

- 调研默认保持中立（总规则第 23 条）。
- 被新调研取代的旧调研移到 `归档/调研/`，不要删。
- `财务/` 是私密的，已经列在 `.claudeignore` 里。只有 {Name} 要看某个具体文件时才打开（总规则第 8 条）。
