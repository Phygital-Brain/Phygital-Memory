Kaalamang naiipon sa paglipas ng panahon: mga desisyon, research, aplikasyon at ang archive.

## Saan ilalagay

| Content | Ilagay sa |
|---|---|
| Desisyon kasama ang dahilan, o pag-aaral sa isang bagay mula sa labas (app, website, kurso, kakumpitensya) | `desisyon/YYYY-MM-DD-{title}.md` |
| Research (market, trend, mga opsyon) | `research/{topic}.md` |
| Aplikasyon: trabaho, grant, parangal, open call (ginagawa sa unang gamit) | `aplikasyon/{name}/` |
| Profile ng kakumpitensya (ginagawa sa unang gamit) | `kakumpitensya/{name}.md` |
| Pera: invoice, buwis, bayad. Pribado | `pera/` |
| Mga naka-archive na desisyon | `archive/desisyon/` |
| Tapos na o lumang research | `archive/research/` |
| Mga tapos nang project | `archive/{name}/` |
| Mga note sa meeting | `desisyon/` kung may lumabas na desisyon, kung wala, ang note ng araw na iyon sa `Araw-araw/`. Magmungkahi lang ng folder para sa meeting kapag marami na. |

## Info block (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: ang petsa ng pagsulat ng note.
- `status`: tingnan sa ibaba para sa mga desisyon at aplikasyon. Lahat ng iba pa: `active` o `closed`.
- `tags`: ang uri, saka ang paksa.
- Opsyonal: `project`, `deadline`, `description` (isang pangungusap, nasa double quotes, huling linya).

## Mga note ng desisyon

Laging isama ang dahilan: sino ang kasali, ano ang nagtulak dito, anong trade-off ang tinanggap. Gamitin ang `> [!important]` para sa mismong desisyon at `> [!warning]` para sa mga alam nang panganib.

May `updated:` din ang mga desisyon, kasunod mismo ng `date:`. Ang `date` ay kung kailan ito ginawa, ang `updated` ay ang huling beses na binalikan o binago ito.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (pinagpapasyahan o ginagawa pa), `waiting` (hinihintay ang ibang tao), `paused`, `closed`.
- Kailangang balikan ang desisyon na lampas 30 araw na ang `updated`. Itinuturo ito ng Taga-ayos ng Utak hanggang ituloy, isara o i-archive ito ni {Name} (bawat isa ay ginagawang petsa ng araw na iyon ang `updated`).
- Ililipat lang ang desisyon sa `archive/desisyon/` kapag sinabi ni {Name}.

## Mga aplikasyon

Isang folder bawat aplikasyon: `aplikasyon/{name}/`, may `README.md` na naglalaman ng deadline, link, status at kung ano ang ipinadala. Katabi nito ang ibang file (mga sagot, statement).

- `status`: `draft`, `submitted`, `accepted`, `rejected` o `withdrawn`.
- Itago ang mga sagot sa markdown. Ang malalaking PDF at slides ay nasa labas ng vault: ibuod ang mga ito sa isang note.

## Mga patakaran

- Neutral ang research kung walang ibang sinabi (pangunahing patakaran 23).
- Ilipat sa `archive/research/` ang research na napalitan na, sa halip na burahin ito.
- Pribado ang `pera/` at nakalista ito sa `.claudeignore`. Buksan lang ito kapag humingi si {Name} ng isang tiyak na file (pangunahing patakaran 8).
