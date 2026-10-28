<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

AI 助手所用技能的笔记和偏好，还有大脑管家。

## 结构

```
技能/{skill-name}/
  {skill-name}.md 或 SKILL.md   这个技能做什么
  notes.md                      {Name} 对这个技能的语气和偏好
  references/                   例子和较长的资料
```

## 已安装

| 技能 | 文件夹 | 做什么 |
|---|---|---|
| 大脑管家 | `大脑管家/` | 每天自动整理，{Name} 要求时做体检 |
| 晨间简报 | `晨间简报/` | 一份简短的当天计划，随时要或每个工作日 |
| 导入 | `导入/` | 把其他应用里的笔记搬进来，先由 {Name} 确认计划 |
| 会前准备 | `会前准备/` | 打电话前的简短准备，根据大脑里的笔记 |
| 思考工具 | `思考工具/` | 挑战一个想法、找规律、找互相矛盾的笔记 |
| 已连接的应用 | `已连接的应用/` | 大脑读取哪些应用，以及相关的规则 |
| No AI Slop | `no-ai-slop/` | 写作检查：把文字改得像人写的，或标出有 AI 味的写法（作者 Peter Yang，MIT 许可证，从不修改） |

## 规则

- 每个技能一个文件夹，名字用 kebab-case（小写加连字符）。
- 新增技能时，在上面的表里加一行。
- 要添加技能或连接应用，先看看 Phygital Brain 的推荐：通过 Phygital Brain 连接器查看 `suggested-skills/README.md` 和 `suggested-apps/README.md`，或者在线打开 https://github.com/Phygital-Brain/phygital-brain/tree/main/skills 查看。如果在里面，就按它的页面来做。{Name} 问“我的大脑还能加点什么？”、“what can I add to my brain?”时，把两份清单都列出来，适合 {Name} 工作的放前面，已经连接的应用和已经安装的技能不用列。
- 别人做的 `SKILL.md` 一律不改。要定制某个技能，就在它的文件夹里加一个 `笔记.md`。
- `大脑管家/每日整理.md` 由定时任务读取。只有要改每日运行做的事时才改它，而且要保持简单：不放链接，不放提示框。
