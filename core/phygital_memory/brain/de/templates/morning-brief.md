---
type: skill
status: active
tags: [morning-brief, planning]
---

Ein kurzer Plan für den Tag. Zwei Varianten: **Briefing** (auf Nachfrage) und **Zeitplan** (an jedem Arbeitstag).

## Briefing

Auslöser: "Morgenbriefing", "morning brief" oder dasselbe auf {Language}.

1. Lies `Tagebuch/aufgaben.md`, die neueste Tagesnotiz, "Stand und nächster Schritt" von jedem Projekt mit `status: active` und die Entscheidungen mit Status `open` oder `waiting`.
2. Wenn ein Kalender verbunden ist, lies die Termine von heute.
3. Antworte in höchstens 6 kurzen Zeilen:
   - Die 3 wichtigsten Dinge für heute, jedes mit einem `[[Link]]` zu seiner Notiz.
   - Worauf {Name} von anderen wartet.
   - Eine Entscheidung, die ansteht, falls es eine gibt.
   - Die Termine von heute, wenn ein Kalender verbunden ist.
4. Schreib keine Datei. Wenn {Name} mit neuen Infos reagiert, speicher sie nach Hauptregel 9.

## Zeitplan

Auslöser: "richte mein Morgenbriefing ein", "set up my morning brief" oder dasselbe auf {Language}.

1. Frag nach der Uhrzeit (Optionen zum Anklicken: 7:00, 8:00, 9:00, 10:00), an den Arbeitstagen von {Name}. Lass die Frage weg, wenn die Uhrzeit schon bei der Einrichtung festgelegt wurde.
2. Leg in der Agent-App eine geplante Aufgabe an, die in diesem Ordner läuft, mit diesem Prompt:

   > Öffne den Ordner mit meinem zweiten Gehirn. Lies `Skills/morgenbriefing/morgenbriefing.md` und gib mir mein Morgenbriefing.

3. Wenn es keine geplanten Aufgaben gibt, sag {Name}, einfach "Morgenbriefing" zu sagen, wenn der Tag losgeht.
