<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

这个文件夹存放关于 {Name} 的核心信息。其他所有工作都以这些笔记为准。

## 文件

| 文件 | 用途 | 分类标签 |
|---|---|---|
| `个人档案.md` | {Name} 是谁、怎么工作、希望 AI 助手怎么配合 | `identity` |
| `个人经历.md` | {Name} 的经历 | `identity` |
| `目标.md` | 目标和优先事项 | `goals` |
| `业务.md` | 业务情况 | `business` |
| `服务.md` | 服务、产品、报价方案 | `business` |
| `客户画像.md` | 谁来买，以及他们怎么找到 {Name} | `customers` |
| `痛点.md` | 要解决的问题 | `customers`（如果 {Name} 不卖东西，就用 `goals`） |
| `品牌.md` | 语气、口吻、要用和要避开的词 | `brand` |
| `工具.md` | 用到的工具，以及各类东西放在哪里 | `tools` |
| `简历.md` | 工作经历、教育背景、媒体报道、获奖 | `career` |

## 信息块（frontmatter）

这里的每个文件（这个文件除外）都以下面的内容开头：

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "{Name} 是谁，希望 AI 助手怎么配合。"
---
```

- `type`：一律是 `about`。
- `status`：`active`；如果已经知道某条信息过时了，就用 `outdated`。
- `updated`：信息最后一次变化的日期。只改错别字或文风时不动它。
- `tags`：先写 `about`，再写上表里这个文件的分类标签，然后写说明文件内容的主题标签（英文、小写、用连字符）。增删章节时，同步更新主题标签。
- `description`：一句话，放在英文双引号里，说明这个文件放了什么。始终放在最后一行。

## 规则

- 这些文件是信息的依据。不要把内容复制到别处，链接过来就行。
- 用“事实汇总”格式（总规则第 17 条）：当前的事实放在最上面，带日期的依据放在下面。
- {Name} 的完整出生日期只记在 `个人档案.md` 里。不要复制它，回复里也不要引用。出生年份可以提。
- 只有新话题需要时才新建文件。先问（总规则第 9 条）。
- 体检时，标出 `目标.md` 里没有进行中项目的目标。
