---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Der Check-up des Aufräumhelfers: ein gründlicher Blick auf das ganze Gehirn, wenn {Name} danach fragt. Nichts wird geändert, bis {Name} Ja sagt. (Das tägliche Aufräumen steht in `täglich.md`.)

Auslöser: "mach einen Check-up von meinem Gehirn", "check up my brain", "räum mein Gehirn auf", "tidy my brain", "Gehirn-Check-up", "brain check-up" oder dasselbe auf {Language}.

## 1. Anschauen (noch nichts ändern)

Durchsuch den ganzen Ordner und liste Probleme in diesen Gruppen auf:

- **Kaputte Links**: `[[Links]]`, die auf Notizen zeigen, die es nicht gibt. Repariere sie nie, indem du eine leere Notiz anlegst: Die echte Notiz wird vielleicht noch synchronisiert (Hauptregel 28).
- **Verwaiste Notizen**: Notizen, auf die keine andere Notiz verlinkt.
- **Leere oder fast leere Notizen** und übrig gebliebene Platzhalter (`[name]`, `TBD`).
- **Falscher Platz**: Dateien direkt im Hauptordner (außer `CLAUDE.md`, `.claudeignore`, `.backups/` und der einzeiligen Regeldatei eines anderen Agenten, etwa `AGENTS.md`), Notizen, die nicht zur Tabelle "Wo was hinkommt" ihres Ordners passen.
- **Veraltete Tabellen "Wo was hinkommt"**: Eine `CLAUDE.md` nennt Dateien oder Ordner, die es nicht gibt, oder lässt welche aus, die es gibt (Zeilen mit "wird bei der ersten Nutzung angelegt" sind okay).
- **Info-Blöcke**: fehlend oder unvollständig, verglichen mit der `CLAUDE.md` des Ordners. Kein `status:`, weniger als 2 `tags:`, eine Projektnotiz ohne `project:`, Tags in Tagesnotizen, die nicht auf der festen Liste stehen.
- **Liegen gebliebene Projekte**: seit 60 Tagen oder länger nicht aktualisiert. Schlag ein Status-Update, `paused` oder Archivieren vor.
- **Ziele ohne Projekt**: Ziele in `Profil/ziele.md` ohne aktives Projekt.
- **Entscheidungen, die geprüft werden müssen**: `updated` liegt mehr als 30 Tage zurück und der Status ist nicht `closed`.
- **Alte Kontakte**: `status: active`, aber `last-contact` liegt mehr als 12 Monate zurück. Schlag `dormant` vor.
- **Alte Aufgaben**: offene Aufgaben in `Tagebuch/aufgaben.md`, die älter als 30 Tage sind.
- **Doppeltes**: dieselben Fakten in mehr als einer Notiz oder zwei Notizen für dieselbe Person oder Firma.
- **Veralteter Stand**: Profil- oder Kontaktseiten, auf denen alte Updates den aktuellen Stand verdecken (Hauptregel 17).
- **Widersprüchliche Regeln**: Regeln in der Haupt-`CLAUDE.md`, die sich gegenseitig widersprechen.
- **Datenschutz**: Passwörter, Schlüssel oder private Nummern in normalen Notizen (Hauptregeln 25 und 26). Nenn die Notiz, nie den Wert.
- **Schreiben**: Gedankenstriche und Muster aus dem Schreibcheck in Notizen.
- **Neue Version**: Vergleiche die Version dieses Gehirns (die erste Zeile der Haupt-`CLAUDE.md`) mit der neuesten Version von Phygital Brain. Wenn du im Web suchen kannst, ist die neueste die letzte Veröffentlichung auf https://github.com/Phygital-Brain/phygital-brain/releases/latest. Wenn nicht, nimm die Version von Phygital Brain, die in deinem Agenten installiert ist, falls du sie siehst. Wenn du es nicht herausfinden kannst, lass diesen Punkt aus.

## 2. Bericht

Eine kurze Liste in einfachen Worten, gruppiert wie oben. Für jedes Problem: die Notiz, was nicht stimmt, die Korrektur, die du vorschlägst. Die einfachen, sicheren Korrekturen kommen zuerst (Gedankenstriche, fehlende Tags, Zeilen in Tabellen "Wo was hinkommt").

Wenn es eine neuere Version gibt, beginne den Bericht mit einer Zeile. Wenn dein Agent sie schon hat: "Es gibt eine neue Version von Phygital Brain. Sag 'aktualisiere mein zweites Gehirn' ('Upgrade my second brain'), um zu sehen, was neu ist." Wenn nicht: "Es gibt eine neue Version von Phygital Brain. Aktualisiere sie zuerst in deinem Agenten, dann sag 'aktualisiere mein zweites Gehirn'."

## 3. Nur korrigieren, was freigegeben ist

Mach vor der ersten Korrektur eine Sicherung von jeder Datei, die du änderst ("Sicherungen und Rückgängig" in der Haupt-`CLAUDE.md`).

Frag (wenn möglich mit Optionen zum Anklicken): **Alle sicheren korrigieren**, **Eins nach dem anderen**, **Nur der Bericht**.

- Lösch oder verschieb nie etwas ohne die Link-Prüfung und ein klares Ja (Hauptregel 21).
- Im Zweifel archivieren statt löschen.
- Schreib eine Zeile in die heutige `Tagebuch/`-Notiz: was geprüft und was korrigiert wurde.
