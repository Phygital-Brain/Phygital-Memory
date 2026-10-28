---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Prohlídka od Správce mozku: důkladný pohled na celý mozek, když o to {Name} požádá. Nic se nemění, dokud {Name} neřekne ano. (Denní úklid je v `denní-úklid.md`.)

Kdy: „zkontroluj mi mozek“, "check up my brain", „ukliď mi v mozku“, "tidy my brain", „prohlídka mozku“, "brain check-up" nebo totéž v jazyce {Language}.

## 1. Podívej se (zatím nic neměň)

Prohledej celou složku a vypiš problémy v těchhle skupinách:

- **Nefunkční odkazy**: `[[odkazy]]`, které vedou na poznámky, jež neexistují. Nikdy je neopravuj vytvořením prázdné poznámky: skutečná poznámka se možná ještě synchronizuje (hlavní pravidlo 28).
- **Osiřelé poznámky**: poznámky, na které žádná jiná poznámka neodkazuje.
- **Prázdné nebo skoro prázdné poznámky** a zapomenuté zástupné texty (`[name]`, `TBD`).
- **Špatné místo**: soubory v hlavní složce (kromě `CLAUDE.md`, `.claudeignore`, `.backups/` a jednořádkového souboru s pravidly pro jiného agenta, jako je `AGENTS.md`), poznámky, které nesedí na tabulku „Co kam patří“ své složky.
- **Zastaralé tabulky „Co kam patří“**: `CLAUDE.md` uvádí soubory nebo složky, které neexistují, nebo chybí ty, které existují (řádky s poznámkou „vznikne při prvním použití“ jsou v pořádku).
- **Informační bloky**: chybí nebo jsou neúplné podle `CLAUDE.md` dané složky. Chybí `status:`, méně než 2 `tags:`, poznámka k projektu bez `project:`, štítky v denních poznámkách mimo pevný seznam.
- **Zaprášené projekty**: žádná úprava 60 a více dní. Navrhni aktualizaci stavu, `paused` nebo archiv.
- **Cíle bez projektu**: cíle v `Profil/cíle.md`, ke kterým není žádný aktivní projekt.
- **Rozhodnutí ke kontrole**: `updated` starší než 30 dní a stav jiný než `closed`.
- **Staré kontakty**: `status: active`, ale `last-contact` starší než 12 měsíců. Navrhni `dormant`.
- **Staré úkoly**: otevřené úkoly v `Deník/úkoly.md` starší než 30 dní.
- **Duplicity**: stejná fakta ve víc poznámkách nebo dvě poznámky pro stejného člověka nebo firmu.
- **Zapadlý aktuální stav**: stránky v profilu nebo v kontaktech, kde staré aktualizace zakrývají to, co platí teď (hlavní pravidlo 17).
- **Pravidla v rozporu**: pravidla v hlavním `CLAUDE.md`, která si navzájem odporují.
- **Soukromí**: hesla, klíče nebo soukromá čísla v obyčejných poznámkách (hlavní pravidla 25 a 26). Uveď poznámku, nikdy samotný údaj.
- **Psaní**: dlouhé pomlčky a vzorce z Kontroly textu v poznámkách.
- **Nová verze**: porovnej verzi tohohle mozku (první řádek hlavního `CLAUDE.md`) s nejnovější verzí Phygital Brain. Když můžeš na web, nejnovější je poslední vydání na https://github.com/Phygital-Brain/phygital-brain/releases/latest. Když nemůžeš, použij verzi Phygital Brain nainstalovanou v tvém agentovi, pokud ji vidíš. Když to nejde zjistit, tenhle bod přeskoč.

## 2. Report

Krátký seznam obyčejnými slovy, rozdělený do skupin jako výše. U každého problému: poznámka, co je špatně a jakou opravu navrhuješ. Jednoduché a bezpečné opravy dej na začátek (dlouhé pomlčky, chybějící štítky, řádky v tabulkách „Co kam patří“).

Když vyšla novější verze, začni report jedním řádkem. Když ji tvůj agent už má: „Vyšla nová verze Phygital Brain. Napiš ‚Aktualizuj můj druhý mozek‘ (nebo 'Upgrade my second brain') a uvidíš, co je nového.“ Když ne: „Vyšla nová verze Phygital Brain. Nejdřív ji aktualizuj ve svém agentovi, pak napiš ‚Aktualizuj můj druhý mozek‘ (nebo 'Upgrade my second brain').“

## 3. Oprav jen to, co je schválené

Před první opravou zazálohuj každý soubor, který budeš měnit (Zálohy a vracení změn v hlavním `CLAUDE.md`).

Zeptej se (s možnostmi na kliknutí, kde to jde): **Opravit všechny bezpečné**, **Projít jednu po druhé**, **Jen report**.

- Nikdy nic nemaž ani nepřesouvej bez kontroly odkazů a jasného ano (hlavní pravidlo 21).
- V případě pochybností archivuj místo mazání.
- Zapiš jeden řádek do dnešní poznámky v `Deník/`: co se zkontrolovalo a co opravilo.
