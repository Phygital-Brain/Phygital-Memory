<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

{Name} 的日记。每天一个文件：`YYYY-MM-DD.md`。没做完的待办放在 `待办.md` 里。

## 信息块（frontmatter）

每篇日记都以这个信息块开头，没有例外。

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
- `date`：日记的日期，`YYYY-MM-DD`。
- `day`：星期几，用英文写（Monday、Tuesday……）。
- `week`：ISO 周数，`WNN`。
- `month`：月份，用英文写（January、February……）。
- `status`：当天还没过完时是 `active`，过去 2 天或更久以后改成 `completed`。
- `tags`：一律有 `daily`，再从下面这份固定列表里挑当天发生过的。绝不自己编别的标签。
  - `problem`：有东西坏了或出了问题
  - `clients`：做客户的活，或和客户联系
  - `meeting`：打电话或开会
  - `money`：发票、付款、税务、投资
  - `research`：做了调研或有了调研结果
  - `decision`：{Name} 做了某个决定
  - `travel`：{Name} 在出差或旅行
  - `personal`：健康、生活等工作以外的事

## 规则

- 日期按总规则第 30 条来（先看电脑的时区，再用 {Time zone}）。
- 谁创建日记（AI 助手或定时任务），谁就先写信息块。没有信息块的日记，下次编辑时在最上面补上。
- 不要写 `# YYYY-MM-DD` 这样的标题。文件名就是标题。
- 日记记录的是当天的最新状态：每天一份整洁的文档，各部分原地更新，绝不堆一串重复的条目。
- 对话记录：一个加粗的标题，加 1 到 2 句话，人和项目写成 `[[双链]]`，细节放进链接到的笔记里。
- 今天的日记只写今天的事。前几天没做完的待办放进 `待办.md`，绝不往后复制。
- 创建今天的日记时，看一下 2、3、4 天前的日记。还是 `status: active` 的改成 `completed`，并从固定列表里给当天明显发生过的事加上标签。不要再往前看。

## `待办.md`

不属于任何项目的待办。项目的待办放在那个项目的 README 里（“现状和下一步”）。第一次用到时创建：

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## 未完成

- [ ] 2026-10-13：把发票发给 [[林晓]]

## 已完成

- [x] 2026-10-12：预约牙医（2026-10-13 完成）
```

- 最新的待办放在最上面，写上添加的日期。
- 待办做完后，打勾，写上完成日期，移到 `## 已完成` 下面。
- 完成超过 30 天的待办可以删掉（先问，总规则第 9 条）。
