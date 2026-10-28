<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Poznámky a preference k dovednostem, které agent používá, a k tomu Správce mozku.

## Struktura

```
Dovednosti/{skill-name}/
  {skill-name}.md nebo SKILL.md   co dovednost dělá
  notes.md                        hlas a preference, které má {Name} pro tuhle dovednost
  references/                     příklady a delší materiály
```

## Nainstalované

| Dovednost | Složka | Co dělá |
|---|---|---|
| Správce mozku | `správce-mozku/` | Každý den sám uklízí a udělá prohlídku, když o ni {Name} požádá |
| Ranní přehled | `ranní-přehled/` | Krátký plán na den, na požádání nebo každý pracovní den |
| Import | `import/` | Přenáší poznámky z jiných aplikací, podle plánu, který {Name} nejdřív schválí |
| Příprava na schůzku | `příprava-na-schůzku/` | Krátký přehled před hovorem, z poznámek v mozku |
| Nástroje na přemýšlení | `přemýšlení/` | Zpochybní nápad, najde vzorce, najde poznámky, které si odporují |
| Propojené aplikace | `propojené-aplikace/` | Ze kterých aplikací mozek čte a jaká pro ně platí pravidla |
| No AI Slop | `no-ai-slop/` | Kontrola textu: upraví text, aby zněl lidsky, nebo označí vzorce typické pro AI (autor Peter Yang, licence MIT, nikdy se neupravuje) |

## Pravidla

- Jedna složka na dovednost, název v kebab-case (malými písmeny se spojovníky).
- Když přibude nová dovednost, přidej řádek do tabulky výše.
- Než přidáš dovednost nebo propojíš aplikaci, podívej se nejdřív na návrhy od Phygital Brain: `suggested-skills/README.md` a `suggested-apps/README.md` přes konektor Phygital Brain, nebo online na https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Pokud to tam je, postupuj podle té stránky. Když se {Name} zeptá „co můžu přidat do svého mozku?“, "what can I add to my brain?", ukaž oba seznamy. Nejdřív to, co se hodí k práci, kterou dělá {Name}, a vynech aplikace, které už jsou propojené, a dovednosti, které už jsou nainstalované.
- `SKILL.md`, který pochází od někoho jiného, se nikdy neupravuje. Když chceš dovednost přizpůsobit, přidej do její složky `poznámky.md`.
- `správce-mozku/denní-úklid.md` čte naplánovaná úloha. Měň ho jen tehdy, když se má změnit, co dělá denní běh, a drž ho jednoduchý: žádné odkazy, žádné zvýrazněné bloky.
