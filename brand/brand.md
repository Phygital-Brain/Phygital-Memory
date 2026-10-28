---
type: brand
date: 2026-10-27
project: Phygital-Memory
status: active
tags: [phygital-memory, brand, visual-identity, design-system]
---

Visual identity for Phygital Memory. Same family as Phygital Brain and Phygital Key: the round seal with one wire ending in sparks, the night ground, flat surfaces, the same three fonts. What changes is the colour pair and the drawing inside the seal. Warm, clear, made by a person. Dark is the default theme. Light is a full second theme.

> [!info] Full guide
> `Phygital-Memory-Brand.pdf` in this folder: cover, colour, type, logo files and rules (3 pages, same layout as Phygital Brain's).

## The idea

The logo is **the Knot**: one wire ties a loop inside the seal, like a string tied round a finger so you remember. Both ends are sparks: you and your agent. The loop is what's held safe between them. Chosen 2026-10-27. Tagline (draft): "Locked notes your agent can remember."

## Colour

Lime is you: your memory, used for the logo, buttons, links and focus. Ultramarine is the spark: your agent at work, a note it opened, a door that needs a yes. Status always carries a word, never colour alone. No other Phygital product uses either colour.

| Role | Dark (default) | Light |
|---|---|---|
| Page ground | `#0B0D12` | `#F4F6F9` |
| Card surface | `#161A22` | `#FFFFFF` |
| Recessed (code, paths) | `#07080C` | `#E6EAF0` |
| Text | `#F1EDE4` | `#0B0D12` |
| Muted text | `#A7A39A` | `#4A5160` |
| Hairline | `#2A303C` | `#D5DAE3` |
| Brand lime (logo, fills) | `#C8F031` | `#C8F031` |
| Lime as interface (buttons, links, focus) | `#C8F031` | `#566E00` |
| Brand ultramarine (logo sparks, fills) | `#4D5BFF` | `#4D5BFF` |
| Ultramarine as interface (agent notes, approvals) | `#8A94FF` | `#3B47E6` |
| Lime tint | `#2A3308` | `#F3FBD9` |
| Ultramarine tint | `#171B45` | `#E8EAFF` |

Bright lime is a logo and fill colour only: as text on a light ground it is 1.2:1, so light mode uses deep lime (5.4:1). Brand ultramarine is too dark for text on night (3.9:1), so dark mode uses `#8A94FF` (7.2:1) and light mode `#3B47E6` (6.0:1). Night text on lime is 14.8:1, white text on ultramarine 4.9:1.

## Type

- Display: Anybody, 800, expanded, uppercase for titles. Card titles: Anybody 700, expanded, sentence case.
- Text: Hanken Grotesk.
- Data: JetBrains Mono, for file names, paths and fields.
- All three load from Google Fonts. Expanded Anybody needs the width axis: `Anybody:wdth,wght@100..150,500..900`. The wordmark files have the letters as shapes, so they need no font.

## Logo files

| File | Use |
|---|---|
| `phygital-memory-mark.svg` | Default. Lime seal, night wire, ultramarine sparks. Both themes. |
| `phygital-memory-mark-night.svg` | Night seal, lime wire. When the mark sits on lime or a very light fill. |
| `phygital-memory-wire-lime.svg` | The wire alone, no seal. Dark grounds. |
| `phygital-memory-wire-ink.svg` | The wire alone, near black with ultramarine sparks. Light grounds and print. |
| `phygital-memory-favicon.svg` | Thicker wire and a simpler knot for small sizes (below 32px). |
| `phygital-memory-wordmark.svg` / `-ink.svg` | Mark and name in one line, for dark / light grounds. |
| `phygital-memory-stacked.svg` / `-ink.svg` | Mark above the name on two lines, for dark / light grounds. |
| `png/app-icon-1024.png`, `png/app-icon.icns` | The Mac app icon: the Knot on a night tile. Also on the `.dmg` and every "Open in Phygital Memory" file. Source: `src/app-icon.html`. |
| `phygital-memory-avatar.png` | GitHub organisation picture (500px). |
| `png/` | `favicon.ico` (16, 32, 48), `favicon-16/32/48.png`, `apple-touch-icon.png` (180), `phygital-memory-mark-512.png`, `social-preview.png` (1280×640). |
| `src/` | Sources: `make-logos.py` (SVGs), `guide.html` (the PDF), `social-preview.html`, `icon.html` and `render.sh` (PNGs, Brave headless). |

Never recolour, redraw or rotate. Below 32px use the favicon file. Write the name exactly as "Phygital Memory".

## Shape and depth

Cards 10px radius, buttons and fields 6px, tags and rows 4px, the seal always round. Flat with a hairline, no gradients or glow.

## Words

Plain and short. Questions and messages say "your agent", never a product name, because the memory works with Claude, ChatGPT, Codex and others.
