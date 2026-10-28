<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Jegyzetek és beállítások az ügynök által használt készségekhez, és itt van a Rendrakó is.

## Felépítés

```
Készségek/{skill-name}/
  {skill-name}.md vagy SKILL.md   mit csinál a készség
  notes.md                        {Name} hangja és kérései ehhez a készséghez
  references/                     példák és hosszabb anyagok
```

## Telepítve

| Készség | Mappa | Mit csinál |
|---|---|---|
| Rendrakó | `rendrakó/` | Minden nap magától rendet rak, és átvizsgálja az agyat, ha {Name} kéri |
| Reggeli összefoglaló | `reggeli-összefoglaló/` | Rövid terv a napra, kérésre vagy minden munkanapon |
| Importálás | `importálás/` | Más appokból hoz át jegyzeteket, egy tervvel, amit előbb {Name} jóváhagy |
| Felkészülés megbeszélésre | `felkészülés-megbeszélésre/` | Rövid összefoglaló egy hívás előtt, az agy jegyzeteiből |
| Gondolkodási eszközök | `gondolkodás/` | Megkérdőjelez egy ötletet, mintákat keres, és megkeresi az egymásnak ellentmondó jegyzeteket |
| Összekapcsolt appok | `összekapcsolt-appok/` | Melyik appokból olvas az agy, és milyen szabályok vonatkoznak rájuk |
| No AI Slop | `no-ai-slop/` | Az Írásellenőrzés: úgy javítja a szöveget, hogy emberi legyen, vagy jelzi az AI-szerű mintákat (Peter Yang munkája, MIT licenc, soha nem módosítjuk) |

## Szabályok

- Minden készségnek egy mappa, kebab-case névvel (kisbetűk, kötőjellel).
- Ha új készség kerül be, adj hozzá egy sort a fenti táblázathoz.
- Ha új készséget adnál hozzá vagy egy appot csatlakoztatnál, előbb nézd meg a Phygital Brain javaslatait: a `suggested-skills/README.md` és a `suggested-apps/README.md` fájlt a Phygital Brain csatlakozóján keresztül, vagy online: https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Ha ott van, kövesd az oldalát. Ha {Name} megkérdezi: "mit adhatok hozzá az agyamhoz?", "what can I add to my brain?", mutasd meg mindkét listát: elöl azokat, amelyek illenek {Name} munkájához, és hagyd ki a már csatlakoztatott appokat és a már telepített készségeket.
- Egy máshonnan származó `SKILL.md` fájlt soha nem módosítunk. Ha egy készséget testre szabnál, tegyél egy `jegyzetek.md` fájlt a mappájába.
- A `rendrakó/napi.md` fájlt egy ütemezett feladat olvassa. Csak akkor módosítsd, ha azon kell változtatni, amit a napi futás csinál, és maradjon egyszerű: se linkek, se kiemelt dobozok.
