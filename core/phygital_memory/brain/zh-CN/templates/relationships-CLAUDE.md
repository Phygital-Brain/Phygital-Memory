<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `客户/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

和 {Name} 打交道的所有人：每个人或机构一篇笔记。

## 子文件夹

| 文件夹 | 放谁 |
|---|---|
| `客户/` | {Name} 为他们交付工作的个人和公司 |
| `合作者/` | 创作上的伙伴，互相交流，不涉及钱 |
| `团队/` | 和 {Name} 一起工作或为 {Name} 工作的人（自由职业者、助理） |
| `合作伙伴/` | 帮 {Name} 打开知名度的机构（媒体、场地、平台） |

## 新的潜在客户放哪

- 第一次接触，还没有真正的需求：在 `客户/_潜在客户.md` 的 `## 新线索` 下写一行（第一次用到时创建）。
- 对方回复说“以后再说”：在 `客户/_潜在客户.md` 的 `## 保持联系` 下写一行。
- 有了真正的需求，或者通话、报价正在进行：建一篇客户笔记 `客户/{client-name}.md`，写 `status: prospect`。

潜在客户往前走一步时，把它移到下一个位置，并从原来的位置删掉。

## 信息块（frontmatter）

这里的每篇笔记（`CLAUDE.md` 文件和 `_潜在客户.md` 除外）都以下面的内容开头：

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "用一句平实的话说明对方是谁，以及和 {Name} 是什么关系。"
---
```

- `type`：`client`、`collaborator`、`team` 或 `partner`。
- `status`：`active`（过去 12 个月内有合作或联系）、`prospect`（在谈，还没合作过）、`dormant`（超过 12 个月没联系）、`closed`（彻底结束了）。
- `last-contact`：最近一次真正联系或合作的月份，格式 `YYYY-MM`。不知道就留空。
- `tags`：先写 `relationship`，再写类型，然后写 2 到 5 个主题标签（行业、国家、工作类型），英文、小写、用连字符。
- `description`：一句话，放在英文双引号里。始终放在最后一行。
- 可选：`aliases`（对方的其他叫法）、`project`（当前的项目）。

## 规则

- **不建重复笔记。** 新建之前，先搜这个名字和它的各种写法（简繁体、拼音或英文名、简称、品牌名和公司名）。如果已经有笔记，就用它，并把新写法加进 `aliases`。同一个人或公司绝不建第二篇笔记。
- **“事实汇总”格式**（总规则第 17 条）：对方是谁、目前的情况放在最上面，带日期的历史放在下面。
- **保持最新。** {Name} 和某人有真正的联系时（一封邮件、一次通话、交付了工作），把 `last-contact` 改成这个月，如果 `status` 变了也一起改。
- **公司里的联系人**（经纪人、经理、编辑）在公司笔记里写成普通文字，绝不写成 `[[链接]]`，也不单独建笔记。在别处提到他们时，链接到公司：`[[公司名|联系人名]]`。
- **私人信息**（电话、邮箱、家庭住址）只写在这个人或公司自己的笔记里。绝不复制到日记或其他笔记里。
- 在项目和日记里用 `[[双链]]` 链接到人。
- 只有出现新的关系类型时，才建新的子文件夹。先问。
